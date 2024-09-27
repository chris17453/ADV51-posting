
# `post_so` Stored Procedure Documentation

## Summary

The `post_so` stored procedure is designed to process sales orders by performing a series of validations, logging mark points, handling transactions with enhanced error logging, and updating relevant records across multiple tables. This procedure ensures data integrity and consistency by implementing idempotency checks and comprehensive error handling mechanisms.

## Table of Contents

- [Summary](#summary)
- [Description](#description)
- [Prerequisites](#prerequisites)
- [Parameters](#parameters)
- [Procedure Steps](#procedure-steps)
  - [1. Parameter Validation](#1-parameter-validation)
  - [2. Transaction Management](#2-transaction-management)
  - [3. Idempotency Check](#3-idempotency-check)
  - [4. Pre-validation Steps](#4-pre-validation-steps)
  - [5. Mark Point Logging](#5-mark-point-header-routines)
  - [6. Per Invoice Line Item Processing](#6-mark-point-per-invoice-line-item-processing)
  - [7. Post-Invoice Level Processing](#7-mark-point-post-invoice-level-processing)
  - [8. Finalization](#8-finalization)
- [Error Handling](#error-handling)
- [Dependencies](#dependencies)
- [Example Usage](#example-usage)
- [SQL Code](#sql-code)

## SQL Code
Below is the updated `post_so` stored procedure incorporating the required changes:

```sql
-- =============================================
-- Author:        Your Name
-- Create date:   YYYY-MM-DD
-- Description:   Process Sales Order and Log Mark Points with Enhanced Error Logging
-- =============================================

CREATE PROCEDURE dbo.post_so (
    @invoiceNum INT,
    @logonCode VARCHAR(20)
)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @currentMarkPoint INT = NULL; -- Variable to track the current mark point

    BEGIN TRYS
        -- =============================
        -- Parameter Validation
        -- =============================

        -- Validate @invoiceNum (must be a positive integer)
        IF @invoiceNum <= 0
        BEGIN
            RAISERROR('Invoice number must be a positive integer.', 16, 1);
            RETURN;
        END

        -- Validate @logonCode length (assuming max length of 20)
        IF LEN(@logonCode) > 20
        BEGIN
            RAISERROR('Logon code exceeds the maximum allowed length of 20 characters.', 16, 1);
            RETURN;
        END

        -- =============================
        -- Start Transaction with SERIALIZABLE Isolation Level
        -- =============================

        SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
        BEGIN TRANSACTION;

        -- =============================
        -- Idempotency Check: Ensure Invoice is Not Already Processed
        -- =============================

        IF EXISTS (
            SELECT 1 
            FROM BKSOMARK 
            WHERE BKSOMARK_INVNM = @invoiceNum
              AND BKSOMARK_MARK = 26 -- Assuming mark point 26 signifies completion
              AND BKSOMARK_DONE = 1
        )
        BEGIN
            RAISERROR('Invoice has already been processed.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- =============================
        -- Pre-validation Steps
        -- =============================

        -- 1. Check Invoice Status
        IF dbo.check_invoice_status(@invoiceNum) = 0
        BEGIN
            RAISERROR('Invoice status is invalid for processing.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 2. Retrieve and Validate Customer
        DECLARE @customer_code VARCHAR(20);
        SELECT @customer_code = BKAR_INV_CUSTCODE
        FROM BKARINV
        WHERE BKAR_INV_NUM = @invoiceNum;

        IF @customer_code IS NULL
        BEGIN
            RAISERROR('Customer code not found for the invoice.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        IF dbo.validate_customer(@customer_code) = 0
        BEGIN
            RAISERROR('Customer is either on hold or has exceeded the credit limit.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 3. Validate Inventory
        IF dbo.validate_inventory(@invoiceNum) = 0
        BEGIN
            RAISERROR('One or more inventory items do not exist or have insufficient stock.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 4. Validate Tax
        IF dbo.validate_tax(@invoiceNum) = 0
        BEGIN
            RAISERROR('Tax amounts do not match the expected values.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 5. Validate Payment Terms
        IF dbo.validate_payment_terms(@invoiceNum) = 0
        BEGIN
            RAISERROR('Payment terms do not match the customer’s default terms.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 6. Retrieve and Validate Salesperson
        DECLARE @salesperson_code VARCHAR(20);
        SELECT @salesperson_code = BKAR_INV_SLSP
        FROM BKARINV
        WHERE BKAR_INV_NUM = @invoiceNum;

        IF @salesperson_code IS NULL
        BEGIN
            RAISERROR('Salesperson code not found for the invoice.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        IF dbo.validate_salesperson(@salesperson_code) = 0
        BEGIN
            RAISERROR('Salesperson is either inactive or does not exist.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 7. Validate RMA
        IF dbo.validate_rma(@invoiceNum) = 0
        BEGIN
            RAISERROR('Approved RMA record not found for the invoice.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- =============================
        -- Mark Point Logging (Functions 1-6)
        -- =============================

        -- 1. Save Accounts Receivable and Customer Record (Markpoint 1 and 2)
        SET @currentMarkPoint = 2;
        EXEC dbo.markpoint_1_and_2_SaveARAndCustomerRecord @invoiceNum;

        -- 2. Save to Accounts Receivable and Check Account (Markpoint 3)
        SET @currentMarkPoint = 3;
        EXEC dbo.markpoint_3_SaveToARAndCheckAccount @invoiceNum;

        -- 3. Post to General Ledger (Markpoint 4)
        SET @currentMarkPoint = 4;
        EXEC dbo.markpoint_4_PostToGL @invoiceNum;

        -- 4. Post Freight to GL (Markpoint 5)
        SET @currentMarkPoint = 5;
        EXEC dbo.markpoint_5_PostFreightToGL @invoiceNum;

        -- 5. Post Fuel to GL (Markpoint 6)
        SET @currentMarkPoint = 6;
        EXEC dbo.markpoint_6_PostFuelToGL @invoiceNum;

        -- =============================
        -- Per Invoice Line Item Processing
        -- =============================

        DECLARE @lineCount INT;
        DECLARE @currentLine INT = 1;

        -- Get total number of lines in the invoice
        SELECT @lineCount = COUNT(*)
        FROM BKARINVL
        WHERE BKAR_INV_NUM = @invoiceNum;

        WHILE @currentLine <= @lineCount
        BEGIN
            -- 7. Update Inventory Location (Markpoint 7)
            SET @currentMarkPoint = 7;
            EXEC dbo.markpoint_7_UpdateInventoryLocation @invoiceNum, @currentLine;

            -- 8. Save to Warehouse (Markpoint 8)
            SET @currentMarkPoint = 8;
            EXEC dbo.markpoint_8_SaveToWarehouse @invoiceNum, @currentLine;

            -- 9. Update Inventory Master (Markpoint 9)
            SET @currentMarkPoint = 9;
            EXEC dbo.markpoint_9_UpdateInventoryMaster @invoiceNum, @currentLine;

            -- 10. Post to Sales Account (Markpoint 10)
            SET @currentMarkPoint = 10;
            EXEC dbo.markpoint_10_PostToSalesAccount @invoiceNum, @currentLine;

            -- 11. Post Restocking and Discounts (Markpoint 11)
            SET @currentMarkPoint = 11;
            DECLARE @discToPost DECIMAL(18,2) = 0; -- Replace with actual discount retrieval logic
            DECLARE @restockAmt DECIMAL(18,2) = 0; -- Replace with actual restocking amount retrieval logic
            EXEC dbo.markpoint_11_PostRestockingAndDiscounts @invoiceNum, @currentLine, @discToPost, @restockAmt;

            -- 12. Post to Other Accounts (Markpoint 12)
            SET @currentMarkPoint = 12;
            EXEC dbo.markpoint_12_PostToOtherAccounts @invoiceNum, @currentLine;

            -- 13. Post Warranty and Scrapped Items (Markpoint 13)
            SET @currentMarkPoint = 13;
            EXEC dbo.markpoint_13_PostWarrantyAndScrappedItems @invoiceNum, @currentLine;

            -- 14. Save Inventory Transaction (Markpoint 14)
            SET @currentMarkPoint = 14;
            EXEC dbo.markpoint_14_SaveInventoryTransaction @invoiceNum, @currentLine, @logonCode;

            -- 15. Post Line Item Freight (Markpoint 15)
            SET @currentMarkPoint = 15;
            EXEC dbo.markpoint_15_PostLineItemFreight @invoiceNum, @currentLine; 

            -- 16. Archive Invoice Line Item (Markpoint 16)
            SET @currentMarkPoint = 16;
            EXEC dbo.markpoint_16_ArchiveInvoiceLineItem @invoiceNum, @currentLine;

            -- 17. Delete Invoice Line Item (Markpoint 17)
            SET @currentMarkPoint = 17;
            EXEC dbo.markpoint_17_DeleteInvoiceLineItem @invoiceNum, @currentLine;

            SET @currentLine = @currentLine + 1;
        END

        -- =============================
        -- Post-Invoice Level Processing
        -- =============================

        -- 18. Update Points History (Markpoint 18)
        SET @currentMarkPoint = 18;
        DECLARE @points_earned FLOAT = 0; -- Replace with actual points earned retrieval logic
        DECLARE @points_class VARCHAR(10) = ''; -- Replace with actual customer class retrieval logic
        DECLARE @points_rate FLOAT = 0; -- Replace with actual points rate retrieval logic
        DECLARE @tot_ext FLOAT = 0; -- Replace with actual total extended amount retrieval logic
        DECLARE @lucky7 CHAR(1) = 'Y'; -- Replace with actual lucky7 flag retrieval logic
        EXEC dbo.Markpoint18_UpdatePointsHistory 
            @invoice_number = @invoiceNum, 
            @points_cust = @customer_code, 
            @points_class = @points_class, 
            @points_rate = @points_rate, 
            @points_earned = @points_earned, 
            @tot_ext = @tot_ext, 
            @lucky7 = @lucky7;

        -- 19. Update Customer Points (Markpoint 19)
        SET @currentMarkPoint = 19;
        EXEC dbo.Markpoint19_UpdateCustomerPoints 
            @invoice_number = @invoiceNum, 
            @points_earned = @points_earned, 
            @points_cust = @customer_code, 
            @lucky7 = @lucky7;

        -- 20. Update Tax Authority (Markpoint 20)
        SET @currentMarkPoint = 20;
        EXEC dbo.Markpoint20_UpdateTaxAuthority @invoiceNum;

        -- 21. Delete Invoice Sales Lines (Markpoint 23)
        SET @currentMarkPoint = 23;
        EXEC dbo.Markpoint23_DeleteInvoiceSalesLines @invoiceNum;

        -- 22. Process Invoice and Update Sales (Markpoint 24)
        SET @currentMarkPoint = 24;
        EXEC dbo.Markpoint24_ProcessInvoiceAndUpdateSales @invoiceNum;

        -- 23. Transfer Invoice to Historical (Markpoint 25)
        SET @currentMarkPoint = 25;
        DECLARE @actualNL INT = 0; -- Replace with actual number line retrieval logic
        EXEC dbo.Markpoint25_TransferInvoiceToHistorical 
            @invoiceNum, 
            @actualNL;

        -- 24. Delete or Update Invoice Header (Markpoint 26)
        SET @currentMarkPoint = 26;
        EXEC dbo.Markpoint26_DeleteOrUpdateInvoiceHeader @invoiceNum;

        -- =============================
        -- Finalization
        -- =============================

        -- Commit Transaction
        COMMIT TRANSACTION;

        -- Update post status
        EXEC dbo.post_status;

    END TRY
    BEGIN CATCH
        -- Handle Errors
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        -- Log the error to the ErrorLog table with InvoiceNumber and MarkPoint
        INSERT INTO dbo._PostingErrorLog (InvoiceNumber, MarkPoint, ErrorMessage, ErrorSeverity, ErrorState)
        VALUES (@invoiceNum, @currentMarkPoint, @ErrorMessage, @ErrorSeverity, @ErrorState);

        -- Re-raise the error to the calling environment
        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH

    RETURN 0;
END;
GO
```

## Description

The `post_so` stored procedure automates the processing of sales orders by:

1. Validating input parameters to ensure data integrity.
2. Managing database transactions with a `SERIALIZABLE` isolation level to prevent data anomalies.
3. Checking for idempotency to avoid duplicate processing of invoices.
4. Performing a series of pre-validation checks on invoice status, customer validity, inventory, tax calculations, payment terms, salesperson validity, and RMA records.
5. Logging mark points to track the progress of the processing steps.
6. Processing each line item in the invoice, including inventory updates, financial postings, and archival.
7. Performing post-invoice level operations such as updating points history, customer points, tax authority records, and transferring invoice data to historical tables.
8. Finalizing the transaction by committing changes and updating the post status.

Comprehensive error handling ensures that any issues encountered during processing are logged appropriately, and transactions are rolled back to maintain data consistency.

## Prerequisites

- **Database Environment:** Microsoft SQL Server.
- **Existing Tables:** `BKSOMARK`, `BKARINV`, `BKARINVL`, `_PostingErrorLog`.
- **Existing Stored Procedures/Functions:** 
  - `check_invoice_status`
  - `validate_customer`
  - `validate_inventory`
  - `validate_tax`
  - `validate_payment_terms`
  - `validate_salesperson`
  - `validate_rma`
  - `markpoint_1_and_2_SaveARAndCustomerRecord`
  - `markpoint_3_SaveToARAndCheckAccount`
  - `markpoint_4_PostToGL`
  - `markpoint_5_PostFreightToGL`
  - `markpoint_6_PostFuelToGL`
  - `markpoint_7_UpdateInventoryLocation`
  - `markpoint_8_SaveToWarehouse`
  - `markpoint_9_UpdateInventoryMaster`
  - `markpoint_10_PostToSalesAccount`
  - `markpoint_11_PostRestockingAndDiscounts`
  - `markpoint_12_PostToOtherAccounts`
  - `markpoint_13_PostWarrantyAndScrappedItems`
  - `markpoint_14_SaveInventoryTransaction`
  - `markpoint_15_PostLineItemFreight`
  - `markpoint_16_ArchiveInvoiceLineItem`
  - `markpoint_17_DeleteInvoiceLineItem`
  - `Markpoint18_UpdatePointsHistory`
  - `Markpoint19_UpdateCustomerPoints`
  - `Markpoint20_UpdateTaxAuthority`
  - `Markpoint23_DeleteInvoiceSalesLines`
  - `Markpoint24_ProcessInvoiceAndUpdateSales`
  - `Markpoint25_TransferInvoiceToHistorical`
  - `Markpoint26_DeleteOrUpdateInvoiceHeader`
  - `post_status`

Ensure all dependencies are created and tested prior to deploying the `post_so` stored procedure.

## Parameters

| Parameter    | Data Type     | Description                                         |
| ------------ | ------------- | --------------------------------------------------- |
| `@invoiceNum` | `INT`         | The unique identifier for the sales invoice. Must be a positive integer. |
| `@logonCode`  | `VARCHAR(20)` | The logon code of the user initiating the procedure. Must not exceed 20 characters. |

## Procedure Steps

### 1. Parameter Validation

- **Invoice Number (`@invoiceNum`):** Ensures it is a positive integer.
- **Logon Code (`@logonCode`):** Ensures it does not exceed 20 characters in length.

### 2. Transaction Management

- Sets the transaction isolation level to `SERIALIZABLE` to prevent concurrent transactions from interfering.
- Begins a database transaction to ensure atomicity of the operations.

### 3. Idempotency Check

- Checks the `BKSOMARK` table to ensure the invoice has not already been processed (mark point 26 with `BKSOMARK_DONE = 1`).
- If already processed, raises an error and rolls back the transaction.

### 4. Pre-validation Steps

Performs a series of validations to ensure the invoice is eligible for processing:

1. **Invoice Status:** Validates using `check_invoice_status`.
2. **Customer Validation:** Retrieves `@customer_code` from `BKARINV` and validates using `validate_customer`.
3. **Inventory Validation:** Ensures inventory items exist and have sufficient stock using `validate_inventory`.
4. **Tax Validation:** Confirms tax amounts match expected values using `validate_tax`.
5. **Payment Terms Validation:** Checks payment terms against customer defaults using `validate_payment_terms`.
6. **Salesperson Validation:** Retrieves and validates `@salesperson_code` using `validate_salesperson`.
7. **RMA Validation:** Ensures an approved RMA record exists using `validate_rma`.

Each failed validation raises an error and rolls back the transaction.

### 5. Mark Point Header Routines

Logs progress at various stages (mark points 1-6) by executing corresponding stored procedures:

1. **Markpoint 1 & 2:** Save Accounts Receivable and Customer Record.
2. **Markpoint 3:** Save to Accounts Receivable and Check Account.
3. **Markpoint 4:** Post to General Ledger.
4. **Markpoint 5:** Post Freight to GL.
5. **Markpoint 6:** Post Fuel to GL.

### 6. Mark point Per Invoice Line Item Processing

Processes each line item in the invoice sequentially:

1. **Markpoint 7:** Update Inventory Location.
2. **Markpoint 8:** Save to Warehouse.
3. **Markpoint 9:** Update Inventory Master.
4. **Markpoint 10:** Post to Sales Account.
5. **Markpoint 11:** Post Restocking and Discounts.
6. **Markpoint 12:** Post to Other Accounts.
7. **Markpoint 13:** Post Warranty and Scrapped Items.
8. **Markpoint 14:** Save Inventory Transaction.
9. **Markpoint 15:** Post Line Item Freight.
10. **Markpoint 16:** Archive Invoice Line Item.
11. **Markpoint 17:** Delete Invoice Line Item.

Each mark point execution updates the `@currentMarkPoint` variable to facilitate error logging.

### 7. Mark point Post-Invoice Level Processing

Performs operations after all line items have been processed:

1. **Markpoint 18:** Update Points History.
2. **Markpoint 19:** Update Customer Points.
3. **Markpoint 20:** Update Tax Authority.
4. **Markpoint 23:** Delete Invoice Sales Lines.
5. **Markpoint 24:** Process Invoice and Update Sales.
6. **Markpoint 25:** Transfer Invoice to Historical.
7. **Markpoint 26:** Delete or Update Invoice Header.

### 8. Finalization

- Commits the transaction to persist all changes.
- Executes `post_status` to update the post status accordingly.

## Error Handling

The procedure employs robust error handling mechanisms:

- **TRY...CATCH Block:** Encapsulates the main processing logic within a `BEGIN TRY` block and catches any exceptions in the `BEGIN CATCH` block.
- **Transaction Rollback:** If an error occurs and a transaction is active, it is rolled back to maintain data integrity.
- **Error Logging:** Errors are logged into the `dbo._PostingErrorLog` table with details including `InvoiceNumber`, `MarkPoint`, `ErrorMessage`, `ErrorSeverity`, and `ErrorState`.
- **Error Propagation:** After logging, the error is re-raised to notify the calling environment of the failure.

## Dependencies

The `post_so` stored procedure relies on several other stored procedures and functions. Ensure the following dependencies are in place before deploying `post_so`:

- **Validation Functions:**
  - `check_invoice_status`
  - `validate_customer`
  - `validate_inventory`
  - `validate_tax`
  - `validate_payment_terms`
  - `validate_salesperson`
  - `validate_rma`

- **Mark Point Procedures:**
  - `markpoint_1_and_2_SaveARAndCustomerRecord`
  - `markpoint_3_SaveToARAndCheckAccount`
  - `markpoint_4_PostToGL`
  - `markpoint_5_PostFreightToGL`
  - `markpoint_6_PostFuelToGL`
  - `markpoint_7_UpdateInventoryLocation`
  - `markpoint_8_SaveToWarehouse`
  - `markpoint_9_UpdateInventoryMaster`
  - `markpoint_10_PostToSalesAccount`
  - `markpoint_11_PostRestockingAndDiscounts`
  - `markpoint_12_PostToOtherAccounts`
  - `markpoint_13_PostWarrantyAndScrappedItems`
  - `markpoint_14_SaveInventoryTransaction`
  - `markpoint_15_PostLineItemFreight`
  - `markpoint_16_ArchiveInvoiceLineItem`
  - `markpoint_17_DeleteInvoiceLineItem`
  - `Markpoint18_UpdatePointsHistory`
  - `Markpoint19_UpdateCustomerPoints`
  - `Markpoint20_UpdateTaxAuthority`
  - `Markpoint23_DeleteInvoiceSalesLines`
  - `Markpoint24_ProcessInvoiceAndUpdateSales`
  - `Markpoint25_TransferInvoiceToHistorical`
  - `Markpoint26_DeleteOrUpdateInvoiceHeader`

- **Error Logging Table:**
  - `dbo._PostingErrorLog`

- **Status Procedure:**
  - `post_status`

## Example Usage

```sql
EXEC dbo.post_so @invoiceNum = 12345, @logonCode = 'USER123';
```


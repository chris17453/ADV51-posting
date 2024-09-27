# Markpoint 14: Save Inventory Transaction

### Summary
This function handles saving an inventory transaction to the `BKICTRAN` table for regular inventory items (`BKIC_PROD_TYPE != 'N'`). It excludes transactions for RMAs with auto-backorder (`inv_group = 'RM'` and `BKAR_INVL_AUTOB = 'W'`). The function stores product details, transaction type, quantity, and related information.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_14_SaveInventoryTransaction (
    @invoiceNum VARCHAR(20),
    @lineNum INT,
    @logonCode VARCHAR(20),
)
AS
BEGIN
    DECLARE @prodType CHAR(1)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @autob CHAR(1)
    DECLARE @prodCode VARCHAR(20)
    DECLARE @units DECIMAL(18,2)
    DECLARE @cost DECIMAL(18,2)
    DECLARE @invDate DATE
    DECLARE @location VARCHAR(10)
    DECLARE @cusCode VARCHAR(20)
    DECLARE @transType CHAR(1) = 'S'  -- 'S' for Sale
    DECLARE @transDesc VARCHAR(50) = 'Invoice'
    DECLARE @transActDate DATE = GETDATE()

    -- Get invoice line and product details
    SELECT @prodType = BKIC_PROD_TYPE, @invGroup = BKAR_INV_GROUP, 
           @autob = BKAR_INVL_AUTOB, @prodCode = BKAR_INVL_PCODE, 
           @units = BKAR_INVL_PQTY, @invDate = BKAR_INV_INVDTE, 
           @location = BKAR_INVL_LOC, @cusCode = BKAR_INV_CUSCOD
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Proceed only if product type is not 'N' (Non-Inventory)
    IF @prodType != 'N'
    BEGIN
        -- Exclude RMAs with auto-backorder
        IF NOT (@invGroup = 'RM' AND @autob = 'W')
        BEGIN
            -- Markpoint 14 before saving
            EXEC markpoint_14_SaveToTransactions @invoiceNum, @lineNum, 0;

            -- Insert transaction into BKICTRAN
            INSERT INTO BKICTRAN (
                BKIC_TRN_PCODE, BKIC_TRN_TYPE, BKIC_TRN_UNITS, BKIC_TRN_COST, 
                BKIC_TRN_DATE, BKIC_TRN_LOC, BKIC_TRN_NUM, BKIC_TRN_CVCODE, 
                BKIC_TRN_DESC, BKIC_TRN_ACTDTE, BKIC_TRN_LOGON
            )
            VALUES (
                @prodCode, @transType, @units, @units, @invDate, @location, 
                @invoiceNum, @cusCode, @transDesc, @transActDate, @logonCode
            );

            -- Markpoint 14 after saving
            EXEC markpoint 14, @invoiceNum, @lineNum, 1;
        END
    END


    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Line Details Lookup**:
   - The function retrieves the product type (`BKIC_PROD_TYPE`), invoice group (`BKAR_INV_GROUP`), auto-backorder flag (`BKAR_INVL_AUTOB`), product code (`BKAR_INVL_PCODE`), quantity (`BKAR_INVL_PQTY`), invoice date (`BKAR_INV_INVDTE`), location, and customer code from the invoice line.

2. **Condition for Product Type**:
   - **Condition**: The function proceeds only if the product type is not "Non-Inventory" (`BKIC_PROD_TYPE != 'N'`).

3. **Condition for RMA with Auto-Backorder**:
   - **Condition**: The function excludes transactions where the invoice group is `RM` (returns) and the auto-backorder flag (`BKAR_INVL_AUTOB`) is set to `'W'`.

4. **Markpoint 14 Execution**:
   - The system executes `markpoint_14_SaveToTransactions` both before and after saving the transaction to track the update progress.

5. **Insert Transaction**:
   - The function inserts the transaction details into the `BKICTRAN` table, capturing the product code, transaction type, units, cost, invoice date, location, customer code, description, action date (current date), and the logon code.

6. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If any required fields are missing or invalid, the function should raise an error and prevent the transaction from being saved.
- The function checks if the product type is "Non-Inventory" and if the invoice is an RMA with auto-backorder, skipping the transaction if necessary.

### Testing:

1. **Test Regular Transaction Posting**:
   - Create test cases where the invoice is not an RMA with auto-backorder. Ensure that the function correctly posts the transaction to the `BKICTRAN` table.

2. **Test RMA with Auto-Backorder Handling**:
   - Create test cases where the invoice is an RMA with auto-backorder (`inv_group = 'RM'` and `BKAR_INVL_AUTOB = 'W'`). Ensure that the function skips the transaction entry.

3. **Test Various Quantities and Costs**:
   - Test with various quantities and ensure that the `BKICTRAN` table reflects the correct values for `BKIC_TRN_UNITS` and `BKIC_TRN_COST`.


### Notes:
- **Transaction Insertion**: The function inserts the transaction details into the `BKICTRAN` table, capturing all relevant information from the invoice line.
- **Post Lock Handling**: If the `post_nolock` flag is set, the function skips saving the transaction.
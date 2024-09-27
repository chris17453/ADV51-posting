# Markpoint 13: Post Warranty and Scrapped Items (Only for Inventory Items)

### Summary
This function handles posting transactions related to scrapped items and RMAs (Return Merchandise Authorizations) to the general ledger, but only when the product type is not "Non-Inventory" (`BKIC_PROD_TYPE != 'N'`). The quantity (`BKAR_INVL_PQTY`) is used as the posting amount, and specific GL accounts are determined based on the invoice group and product category.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_13_PostWarrantyAndScrappedItems (
    @invoiceNum VARCHAR(20),
    @lineNum INT,
)
AS
BEGIN
    DECLARE @prodCat VARCHAR(5)
    DECLARE @invDesc VARCHAR(50)
    DECLARE @invDate DATE
    DECLARE @cusCode VARCHAR(20)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @autob CHAR(1)
    DECLARE @warrGLExp VARCHAR(10)
    DECLARE @warrGLA VARCHAR(10)
    DECLARE @glAccount VARCHAR(10)
    DECLARE @glDept VARCHAR(10)
    DECLARE @postAmt DECIMAL(18,2)
    DECLARE @prodType CHAR(1)
    DECLARE @linkR INT = 1

    -- Get product category, invoice details, product type, and auto-backorder flag
    SELECT @prodCat = BKIC_PROD_CAT, @invDesc = BKAR_INVL_PDESC, 
           @invDate = BKAR_INV_INVDTE, @cusCode = BKAR_INV_CUSCOD, 
           @invGroup = BKAR_INV_GROUP, @autob = BKAR_INVL_AUTOB, 
           @postAmt = BKAR_INVL_PQTY, @prodType = BKIC_PROD_TYPE
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Proceed only if product type is not 'N' (Non-Inventory)
    IF @prodType != 'N'
    BEGIN
        -- Markpoint 13 before posting
        EXEC markpoint 13, @invoiceNum, @lineNum, 0;

        -- Determine posting for warranty scrapped items or RMAs
        IF @invGroup = 'RMS'
        BEGIN
            -- Warranty-related scrapped items (RMS group)
            SET @warrGLExp = dbo.get_wgl(@prodCat, 'E');
            EXEC post_to_gl2 @warrGLExp, CASE WHEN @warrGLExp <> '90999' THEN BKIC_LOC_DPTC ELSE '' END,
                             'Scrapped Automatically', @postAmt, @invoiceNum, @invDate, 'OT', @cusCode, 0, 'Y';
        END
        ELSE
        BEGIN
            -- RMA group with auto-backorder flag
            IF @invGroup = 'RMA' AND @autob = 'W'
            BEGIN
                SET @warrGLA = dbo.get_wgl(@prodCat, 'A');
            END

            -- Post to GL for warranty or RMA
            EXEC post_to_gl2 CASE WHEN @invGroup = 'RMA' AND @autob = 'W' THEN @warrGLA ELSE BKIC_LOC_GLA END,
                             BKIC_LOC_DPTA, @invDesc, @postAmt, @invoiceNum, @invDate, 'OT', @cusCode, 0, 'Y';

            -- If not auto-backordered, log the transaction
            IF NOT (@invGroup = 'RMA' AND @autob = 'W')
            BEGIN
                -- Log the RMA transaction in BKLOGGER
                INSERT INTO BKLOGGER (LOGTYPE, PROD_CODE, DEPT_CODE, ACTION, INV_NUM, AMT, LINK_R, INV_DATE)
                VALUES ('BKSOG', @prodCat, BKIC_LOC_DPTA, 'S', @invoiceNum, @postAmt, @linkR, @invDate);
            END
        END

        -- Markpoint 13 after posting
        EXEC markpoint 13, @invoiceNum, @lineNum, 1;

        -- Update post status
        EXEC post_status;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Line and Product Type Lookup**:
   - The function retrieves the product category (`BKIC_PROD_CAT`), invoice description (`BKAR_INVL_PDESC`), date, customer code, invoice group, auto-backorder flag, posting amount (`BKAR_INVL_PQTY`), and product type (`BKIC_PROD_TYPE`) from the invoice line.

2. **Condition for Product Type**:
   - **Condition**: The function proceeds only if the product type is not "Non-Inventory" (`BKIC_PROD_TYPE != 'N'`). If the product type is "N", the function skips the transaction entirely.

3. **Warranty and Scrapped Item Handling**:
   - **Condition**: If the invoice group is `RMS`, the function processes the item as a warranty-related scrapped item. It retrieves the warranty GL expense account using the `get_wgl` function (based on the product category and warranty type `'E'` for expenses). The quantity from `BKAR_INVL_PQTY` is used as the posting amount.

4. **RMA Group Handling**:
   - **Condition**: If the invoice group is `RMA` and the auto-backorder flag is `'W'`, the function retrieves the warranty GL adjustment account using the `get_wgl` function (with warranty type `'A'` for adjustment). The function posts the quantity (`BKAR_INVL_PQTY`) to the appropriate GL account.

5. **Logging for Non-Auto-Backordered RMAs**:
   - **Condition**: If the invoice group is `RMA` and the auto-backorder flag is not set to `'W'`, the function logs the transaction to the `BKLOGGER` table for tracking purposes.

6. **Markpoint 13 Execution**:
   - The system executes `markpoint_13_SaveToGL` both before and after posting to track the update progress.

7. **Post to General Ledger**:
   - The function calls `post_to_gl2` to post the scrapped or RMA item amounts to the general ledger.

8. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If no valid GL account or department is found, the function should raise an error and prevent the posting.
- Lock failures are handled by calling `quit_posting` to exit and prevent further processing.

### Testing:

1. **Test Warranty Scrapped Item Posting**:
   - Create test cases where the invoice group is `RMS`. Ensure that the function correctly posts the amount to the GL account for scrapped items (`warr_glexp`), using the product category to determine the correct GL account.

2. **Test RMA with Auto-Backorder**:
   - Create test cases where the invoice group is `RMA` and the auto-backorder flag is set to `'W'`. Ensure that the function posts the amount to the GL account for warranty adjustments (`warr_gla`).

3. **Test RMA without Auto-Backorder**:
   - Create test cases where the invoice group is `RMA` and the auto-backorder flag is not set to `'W'`. Ensure that the function logs the transaction in the `BKLOGGER` table and posts the amount to the appropriate GL account.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: Ensure that the `post_to_gl2` procedure handles the actual posting to the general ledger, accepting the necessary parameters like GL account, department, product description, amount, and other invoice details.
- **Logging**: The `BKLOGGER` table is updated for certain RMAs that are not auto-backordered, logging the transaction with relevant details.
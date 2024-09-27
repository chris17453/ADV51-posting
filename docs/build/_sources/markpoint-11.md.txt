# Markpoint 11: Post Restocking Fees and Discounts

### Summary
This function posts discount amounts (PD, WC, AC) and restocking fees to the general ledger. It processes different discount types based on product categories and shipping methods and handles restocking amounts for returns (RMA). The appropriate general ledger accounts and department codes are assigned based on the discount type and the invoice details.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_11_PostRestockingAndDiscounts (
    @invoiceNum VARCHAR(20),
    @lineNum INT,
    @discToPost DECIMAL(18,2),
    @restockAmt DECIMAL(18,2)
)
AS
BEGIN
    DECLARE @locCode VARCHAR(10)
    DECLARE @prodCode VARCHAR(20)
    DECLARE @invDesc VARCHAR(50)
    DECLARE @invDate DATE
    DECLARE @cusCode VARCHAR(20)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @postType VARCHAR(10)
    DECLARE @locDept VARCHAR(10)
    DECLARE @prodCat VARCHAR(5)
    DECLARE @prodFam VARCHAR(5)
    DECLARE @shipVia VARCHAR(50)
    DECLARE @pdAmt DECIMAL(18,2) = 0
    DECLARE @wcAmt DECIMAL(18,2) = 0
    DECLARE @acAmt DECIMAL(18,2) = 0

    -- Get invoice and product details
    SELECT @locCode = BKAR_INVL_LOC, @prodCode = BKAR_INVL_PCODE, 
           @invDesc = BKAR_INVL_PDESC, @invDate = BKAR_INV_INVDTE, 
           @cusCode = BKAR_INV_CUSCOD, @invGroup = BKAR_INV_GROUP,
           @shipVia = BKAR_INV_SHPVIA
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Get location department for the GL posting
    SELECT @locDept = BKMP_LOCS_GLDPT
    FROM BKMPLOCS
    WHERE BKMP_LOCS_LOC = @locCode;

    -- Process discounts if applicable
    IF @discToPost <> 0
    BEGIN
        IF @pdAmt <> 0
        BEGIN
            EXEC post_to_gl2 '40807', @locDept, 'PD disc: ' + @prodCode, @pdAmt, @invoiceNum, @invDate, @postType, @cusCode, 0, 'Y';
        END

        IF @wcAmt <> 0
        BEGIN
            EXEC post_to_gl2 '40801', @locDept, 'WC disc: ' + @prodCode, @wcAmt, @invoiceNum, @invDate, @postType, @cusCode, 0, 'Y';
        END

        IF @acAmt <> 0
        BEGIN
            EXEC post_to_gl2 '40808', @locDept, 'AC disc: ' + @prodCode, @acAmt, @invoiceNum, @invDate, @postType, @cusCode, 0, 'Y';
        END
    END

    -- Handle WC discount separately if there is no specific discount to post
    IF @wcAmt <> 0
    BEGIN
        -- Get product category and family
        SELECT @prodCat = BKIC_CAT_CAT, @prodFam = BKIC_CAT_FMLY
        FROM BKICCAT
        WHERE BKIC_CAT_CAT = @prodCode;

        -- If product family is 'AC' and shipping is not 'WILL CALL', post to AC account
        IF @prodFam = 'AC' AND LEFT(@shipVia, 9) <> 'WILL CALL'
        BEGIN
            EXEC post_to_gl2 '40808', @locDept, 'AC disc: ' + @prodCode, @wcAmt, @invoiceNum, @invDate, @postType, @cusCode, 0, 'Y';
        END
        ELSE
        BEGIN
            -- Otherwise, post to WC account
            EXEC post_to_gl2 '40801', @locDept, 'WC disc: ' + @prodCode, @wcAmt, @invoiceNum, @invDate, @postType, @cusCode, 0, 'Y';
        END
    END

    -- Handle restocking fee for returns (RMA)
    IF @invGroup = 'RM' AND @restockAmt <> 0
    BEGIN
        -- Markpoint 11 before posting
        EXEC markpoint_11_SaveToGL @invoiceNum, @lineNum, 0;

        -- Post restocking fee to general ledger
        EXEC post_to_gl2 '40700', @locDept, @invDesc, @restockAmt, @invoiceNum, @invDate, @postType, @cusCode, 0, 'Y';

       
        -- Markpoint 11 after posting
        EXEC markpoint_11_SaveToGL @invoiceNum, @lineNum, 1;

    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice and Product Lookup**:
   - The function retrieves the product code, invoice description, invoice date, customer code, invoice group, and shipping method from the invoice line.

2. **Location Department Lookup**:
   - The function retrieves the location department (`BKMP_LOCS_GLDPT`) for the general ledger posting based on the invoice location.

3. **Discount Posting**:
   - **Condition**: If the discount amount to post (`disc_to_post`) is not zero, the function checks if there are specific amounts for PD, WC, and AC discounts.
     - **PD Discount**: If there is a `pd_amt`, it is posted to the GL account `40807`.
     - **WC Discount**: If there is a `wc_amt`, it is posted to the GL account `40801`.
     - **AC Discount**: If there is an `ac_amt`, it is posted to the GL account `40808`.

4. **WC Discount Handling**:
   - If there is no specific discount to post but there is a `wc_amt`, the function checks the product family:
     - If the product family is `AC` and the shipping method is not `WILL CALL`, the WC discount is posted to the GL account `40808`.
     - Otherwise, it is posted to `40801`.

5. **Restocking Fee Handling**:
   - **Condition**: If the invoice group is `RM` (returns) and there is a restocking amount (`restock_amt`), the function posts the restocking fee to the GL account `40700`.

6. **Markpoint 11 Execution**:
   - The system executes `markpoint_11_SaveToGL` both before and after posting to track the update progress.

7. **Post to General Ledger**:
   - The function calls `post_to_gl2` to post the relevant amounts to the general ledger for discounts and restocking fees.

8. **Lock Handling**:
   - If the `post_nolock` flag is not set, the function clears buffers and exits without completing the post.

### Error Handling:
- If no location department or discount amounts are available, the function should raise an error and prevent the posting.
- Lock failures are handled by calling `quit_posting` to exit and prevent further processing.

### Testing:

1. **Test Discount Posting**:
   - Create test cases where the discount amount (`disc_to_post`) is not zero. Ensure that the function correctly posts PD, WC, and AC discounts to the appropriate GL accounts.

2. **Test WC Discount Handling**:
   - Create test cases where there is a WC discount and verify that the correct GL account (`40808` for AC product family and `40801` otherwise) is used based on the product family and shipping method.

3. **Test Restocking Fee Posting**:
   - Create test cases where the invoice group is `RM` and a restocking amount is provided. Ensure that the function correctly posts the restocking fee to the GL account `40700`.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: This procedure handles the actual posting of discounts and restocking fees to the general ledger. Ensure that it accepts the correct parameters: GL account, department, product description, amount, invoice number, and other necessary information.
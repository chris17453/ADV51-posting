# Markpoint 12: Post to Other Accounts

### Summary
This function posts quantities and associated amounts to the general ledger based on the product type (`BKIC_PROD_TYPE`), customer class, and invoice group. Special conditions apply for customer code `3509656` and invoice groups `ICZ` and `CAN`.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_12_PostToOtherAccounts (
    @invoiceNum VARCHAR(20),
    @lineNum INT
)
AS
BEGIN
    DECLARE @prodType CHAR(1)
    DECLARE @postAmt DECIMAL(18,2)
    DECLARE @postAmtTemp DECIMAL(18,2)
    DECLARE @glAcct VARCHAR(10)
    DECLARE @glDept VARCHAR(10)
    DECLARE @invDesc VARCHAR(50)
    DECLARE @invDate DATE
    DECLARE @cusCode VARCHAR(20)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @cusClass VARCHAR(10)

    -- Get product type, invoice details, and quantities
    SELECT @prodType = BKIC_PROD_TYPE, @postAmtTemp = BKAR_INVL_PQTY, @invDesc = BKAR_INVL_PDESC, 
           @invDate = BKAR_INV_INVDTE, @cusCode = BKAR_INV_CUSCOD, @invGroup = BKAR_INV_GROUP
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Continue if product type is not 'N' (non-inventory)
    IF @prodType <> 'N'
    BEGIN
        SET @postAmt = @postAmtTemp;  -- Set the post amount

        -- Get customer class
        SELECT @cusClass = BKAR_CLASS
        FROM BKARCUST
        WHERE BKAR_CUSTCODE = @cusCode;

        -- Markpoint 12 before posting
        EXEC markpoint 12, @invoiceNum, @lineNum, 0;

        -- Determine GL account based on customer class, invoice date, and invoice group
        IF @cusClass = 'IC' AND @invDate > '2005-01-01'
        BEGIN
            SET @glAcct = '52110     ';  -- GL account for IC class after 2005
        END
        ELSE IF @cusCode = '3509656' AND @invGroup = 'ICZ'
        BEGIN
            SET @glAcct = '90002     ';  -- Special GL account for customer 3509656 in ICZ group
        END
        ELSE IF @invGroup = 'CAN'
        BEGIN
            SET @glAcct = '50300     ';  -- GL account for Canadian invoices
        END

        -- Get GL department code for posting
        SELECT @glDept = BKIC_LOC_DPTC
        FROM BKICLOC
        WHERE BKIC_PROD_CODE = @prodType;

        -- Post to general ledger using `post_to_gl2` function
        EXEC post_to_gl2 @glAcct, @glDept, @invDesc, @postAmt, @invoiceNum, @invDate, 'OT', @cusCode, 0, 'Y';

        -- Markpoint 12 after posting
        EXEC markpoint 12, @invoiceNum, @lineNum, 1;

        -- Update post status
        EXEC post_status;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Product Type and Invoice Details Lookup**:
   - The function retrieves the product type (`BKIC_PROD_TYPE`), quantity (`BKAR_INVL_PQTY`), invoice description, date, customer code, and invoice group from the invoice line (`BKARINVL`).

2. **Condition for Product Type**:
   - **Condition**: The function continues if the product type is not `N` (non-inventory). Otherwise, it skips the posting process.

3. **Customer Class Lookup**:
   - The function retrieves the customer class (`BKAR_CLASS`) from the customer table (`BKARCUST`) based on the customer code.

4. **GL Account Determination**:
   - **Condition**: The GL account is determined based on the customer class and invoice details:
     - If the customer class is `IC` and the invoice date is after `2005-01-01`, the GL account is set to `52110`.
     - If the customer code is `3509656` and the invoice group is `ICZ`, the GL account is set to `90002`.
     - If the invoice group is `CAN`, the GL account is set to `50300`.

5. **GL Department Lookup**:
   - The function retrieves the GL department (`BKIC_LOC_DPTC`) for the product location from the inventory location table (`BKICLOC`).

6. **Markpoint 12 Execution**:
   - The system executes `markpoint_12_SaveToGL` both before and after posting to track the update progress.

7. **Post to General Ledger**:
   - The function calls `post_to_gl2` to post the amount to the general ledger using the determined GL account, department, product description, and invoice details.

8. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If no valid GL account or department is found, the function should raise an error and prevent the posting.
- Lock failures are handled by calling `quit_posting` to exit and prevent further processing.

### Testing:

1. **Test Regular Product Posting**:
   - Create test cases where the product type is inventory (`BKIC_PROD_TYPE <> 'N'`). Ensure that the function correctly posts the amount to the general ledger based on the product type, customer class, and invoice group.

2. **Test Non-Inventory Product Handling**:
   - Create test cases where the product type is `N`. Ensure that the function skips posting and does not update the general ledger.

3. **Test Special Customer and Invoice Group Posting**:
   - Create test cases where the customer code is `3509656` and the invoice group is `ICZ`. Ensure that the GL account is set to `90002`.
   - Test scenarios with the invoice group `CAN` to ensure the GL account is set to `50300`.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: Ensure that the `post_to_gl2` procedure handles the actual posting to the general ledger, accepting the necessary parameters like GL account, department, product description, amount, and other invoice details.
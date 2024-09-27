# Markpoint 10: Post to Sales Account

### Summary
This function posts entries to the general ledger based on the product type (`BKIC_PROD_TYPE`) and customer class (`BKAR_CLASS`). It uses different general ledger (GL) accounts and department codes depending on whether the product is inventory or non-inventory and based on the customer's classification. It also handles specific conditions for certain customers, invoice groups, and locations.
- This is a PER INVOICE LINE item iteration.


### SQL Function

```sql
CREATE PROCEDURE markpoint_10_PostToSalesAccount (
    @invoiceNum VARCHAR(20),
    @lineNum INT
)
AS
BEGIN
    DECLARE @prodType CHAR(1)
    DECLARE @invType CHAR(1)
    DECLARE @locCode VARCHAR(3)
    DECLARE @cusClass VARCHAR(10)
    DECLARE @cusCode VARCHAR(20)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @invDate DATE
    DECLARE @prodCode VARCHAR(20)
    DECLARE @glAcct VARCHAR(10)
    DECLARE @glDept VARCHAR(10)
    DECLARE @amtToPost DECIMAL(18,2)
    DECLARE @post_nolock BIT = 0

    -- Get invoice line details
    SELECT @prodType = BKIC_PROD_TYPE, @invType = BKAR_INVL_ITYPE, @locCode = LEFT(BKAR_INVL_LOC, 3), 
           @cusCode = BKAR_INV_CUSCOD, @invGroup = BKAR_INV_GROUP, @invDate = BKAR_INV_INVDTE,
           @prodCode = BKAR_INVL_PCODE
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Update department codes for non-inventory items
    IF @prodType = 'N' OR @invType = 'N'
    BEGIN
        UPDATE BKICMSTR
        SET BKIC_PROD_DPTNT = @locCode, BKIC_PROD_DPTS = @locCode
        WHERE BKIC_PROD_CODE = @prodCode;
    END

    -- Get customer class
    SELECT @cusClass = BKAR_CLASS
    FROM BKARCUST
    WHERE BKAR_CUSTCODE = @cusCode;

    -- Determine GL account and department based on customer class and product type
    IF @cusClass <> 'GP'
    BEGIN
        IF @cusClass = 'IC' AND @invDate > '2005-01-01' AND @prodCode NOT IN ('FREIGHT2CANADA', 'FREIGHT2USA')
        BEGIN
            SET @glAcct = '42110     ';
        END
        ELSE IF @cusCode = '3509656' AND @invGroup = 'ICZ'
        BEGIN
            SET @glAcct = '90002     ';
        END
        ELSE
        BEGIN
            SET @glAcct = CASE WHEN @prodType <> 'N' THEN BKIC_LOC_GLSNT ELSE BKIC_PROD_GLSNT END;
            SET @glDept = CASE WHEN @prodType <> 'N' THEN BKIC_LOC_DPTSNT ELSE BKIC_PROD_DPTNT END;
        END
    END
    ELSE
    BEGIN
        IF @cusCode = '3509656' AND @invGroup = 'ICZ'
        BEGIN
            SET @glAcct = '90002     ';
        END
        ELSE
        BEGIN
            SET @glAcct = CASE WHEN @prodType <> 'N' THEN BKIC_LOC_GLS ELSE BKIC_PROD_GLS END;
            SET @glDept = CASE WHEN @prodType <> 'N' THEN BKIC_LOC_DPTS ELSE BKIC_PROD_DPTS END;
        END
    END

    -- Handle special locations ('HQ1', 'HQ2', 'HQ3')
    IF @locCode IN ('HQ1', 'HQ2', 'HQ3')
    BEGIN
        SET @glDept = 'HQ ';
    END

    -- Markpoint 10 before posting
    EXEC markpoint_10_SaveToSales @invoiceNum, @lineNum, 0;

    -- Call procedure to calculate post amounts
    EXEC calc_post_amts @invoiceNum, @lineNum, @amtToPost OUTPUT;

    -- Post to general ledger using `post_to_gl2` function
    EXEC post_to_gl2 @glAcct, @glDept, @prodCode, @amtToPost, @invoiceNum, GETDATE(), 'SALE', NULL, 0, 'Y';

    -- Post lock check
    IF @post_nolock = 0
    BEGIN
        -- Clear inventory master and location handles if necessary
        RETURN quit_posting(9, @lineNum);
    END

    -- Markpoint 10 after posting
    EXEC markpoint_10_SaveToSales @invoiceNum, @lineNum, 1;

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Line Details Lookup**:
   - The function retrieves the product type (`BKIC_PROD_TYPE`), inventory type (`BKAR_INVL_ITYPE`), location code (`BKAR_INVL_LOC`), customer code, invoice group, invoice date, and product code from the invoice line (`BKARINVL`).

2. **Update Department Codes for Non-Inventory Items**:
   - **Condition**: If the product type or inventory type is `N` (non-inventory), the function updates the department codes (`BKIC_PROD_DPTNT`, `BKIC_PROD_DPTS`) based on the invoice location.

3. **Customer Class Lookup**:
   - The function retrieves the customer class (`BKAR_CLASS`) from the customer (`BKARCUST`) table based on the customer code.

4. **Determine GL Account and Department**:
   - **Condition**: Based on the customer class and product type, the function sets the general ledger (GL) account and department:
     - If the customer class is `IC` and the invoice date is after `2005-01-01`, and the product is not one of `FREIGHT2CANADA` or `FREIGHT2USA`, the GL account is set to `'42110'`.
     - If the customer code is `'3509656'` and the invoice group is `ICZ`, the GL account is set to `'90002'`.
     - Otherwise, the GL account and department are set based on whether the product type is inventory or non-inventory.

5. **Special Location Handling**:
   - **Condition**: If the invoice location is `HQ1`, `HQ2`, or `HQ3`, the department code is set to `'HQ'`.

6. **Markpoint 10 Execution**:
   - The system executes `markpoint_10_SaveToSales` both before and after posting to track the update progress.

7. **Post to General Ledger**:
   - The function calls `post_to_gl2` to post the sales details to the general ledger, including the GL account, department, product description, and amount to post.

8. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears the inventory master and location buffers and exits without completing the post.

### Error Handling:
- If the GL account or department cannot be determined based on the provided criteria, the function should raise an error and prevent the posting.
- Lock failures are handled by calling `quit_posting` to exit and prevent further processing.

### Testing:

1. **Test Regular Product Posting**:
   - Create test cases where the product type is inventory (`BKIC_PROD_TYPE <> 'N'`) and the customer class is `IC` or `GP`. Ensure that the function correctly assigns the GL account and department based on the product type and customer class.

2. **Test Non-Inventory Product Posting**:
   - Create test cases where the product type or inventory type is `N`. Ensure that the department codes are updated correctly, and the appropriate GL account is assigned.

3. **Test Special Customers and Invoice Groups**:
   - Create test cases where the customer code is `'3509656'` and the invoice group is `ICZ`. Ensure that the GL account is set to `'90002'`.

4. **Test Special Locations**:
   - Create test cases where the invoice location is `HQ1`, `HQ2`, or `HQ3`. Ensure that the department code is set to `'HQ'`.

5. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: This procedure handles the actual posting of sales details to the general ledger. Ensure that it accepts the correct parameters: GL account, department, product description, amount, invoice number, and other necessary information.
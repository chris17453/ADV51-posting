# Markpoint 15: Post Line Item Freight Charges

### Summary
This function handles posting the freight charges associated with a line item to the general ledger, provided that the freight charge is not zero (`BKAR_INVL_FRGT != 0`). It uses the general ledger freight account (`frght_glacct`) and department (`BKSY_AR_FRGTDPT`).
- This is a PER INVOICE LINE item iteration.

This is actualy something that happens After mark point 14, and has no markpoint of its own.. and the REAL markpoint 15 is discontinued...


### SQL Function

```sql
CREATE PROCEDURE markpoint_15_PostLineItemFreight (
    @invoiceNum VARCHAR(20),
    @lineNum INT,
)
AS
BEGIN
    DECLARE @freight DECIMAL(18,2)
    DECLARE @units DECIMAL(18,2)
    DECLARE @freightGLAcct VARCHAR(10)
    DECLARE @freightDept VARCHAR(10)
    DECLARE @prodDesc VARCHAR(50)
    DECLARE @invDate DATE
    DECLARE @cusCode VARCHAR(20)

    -- Get line item freight details
    SELECT @freight = BKAR_INVL_FRGT, @units = BKAR_INVL_PQTY, 
           @prodDesc = 'Freight from Invoice', @invDate = BKAR_INV_INVDTE, 
           @cusCode = BKAR_INV_CUSCOD
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Only proceed if freight is not zero
    IF @freight != 0
    BEGIN
        EXEC markpoint 15, @invoiceNum, @lineNum, 0;
        -- Call the get_frght_gl subroutine to get the freight GL account and department
        EXEC get_frght_gl @invoiceNum, @lineNum, @freightGLAcct OUTPUT, @freightDept OUTPUT;

        -- Markpoint 15.2 before posting
        EXEC markpoint_15_2_SaveToGL @invoiceNum, @lineNum, 0;

        -- Post to General Ledger for freight
        EXEC post_to_gl2 @freightGLAcct, @freightDept, @prodDesc, @units, 
                         @invoiceNum, @invDate, 'FR', @cusCode, 0, 'Y';

        -- Markpoint 15 after posting
        EXEC markpoint 15, @invoiceNum, @lineNum, 1;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Line Item Lookup**:
   - The function retrieves the freight amount (`BKAR_INVL_FRGT`), units (`BKAR_INVL_PQTY`), invoice date, and customer code from the invoice line.

2. **Condition for Freight Charge**:
   - **Condition**: The function proceeds only if the freight amount is not zero (`BKAR_INVL_FRGT != 0`).

3. **Get Freight GL Account**:
   - The function calls the `get_frght_gl` subroutine to retrieve the appropriate freight GL account (`frght_glacct`) and department (`BKSY_AR_FRGTDPT`) for posting.

4. **Markpoint 15.2 Execution**:
   - The system executes `markpoint_15_2_SaveToGL` both before and after posting to track the update progress.

5. **Post to General Ledger**:
   - The function calls `post_to_gl2` to post the freight charges to the general ledger using the freight GL account, department, and line item details.

6. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If the freight GL account or department is invalid, the function should raise an error and prevent the posting.
- If the freight amount is zero, the function skips posting.

### Testing:

1. **Test Freight Charge Posting**:
   - Create test cases where the line item includes freight charges (`BKAR_INVL_FRGT != 0`). Ensure that the function correctly posts the freight to the GL account.

2. **Test Zero Freight Charge**:
   - Test cases where no freight charge is applied (`BKAR_INVL_FRGT = 0`). Ensure that the function skips the posting.

### Notes:
- **Freight GL Account**: Ensure that the `get_frght_gl` subroutine is properly implemented and retrieves the correct freight GL account and department.
- **Post to General Ledger (`post_to_gl2`)**: Ensure that the `post_to_gl2` procedure handles the actual posting to the general ledger, accepting the necessary parameters like GL account, department, product description, amount, and other invoice details.
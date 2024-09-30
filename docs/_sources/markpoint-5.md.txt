# Markpoint 5: Post Freight Charges

 ### Summary
This function posts freight charges to the general ledger if the freight amount is not zero. The general ledger account is selected based on the customer class and the invoice group. If the customer class is `IC`, `GP`, or if the invoice group is `CAN`, specific GL accounts are used. The department code for freight is based on the invoice location.

### SQL Function

```sql
CREATE PROCEDURE markpoint_5_PostFreightToGL (
    @invoiceNum VARCHAR(20)
)
AS
BEGIN
    DECLARE @frght_glacct VARCHAR(10)
    DECLARE @invFrght DECIMAL(18,2)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @invLoc VARCHAR(3)
    DECLARE @cusClass VARCHAR(10)
    DECLARE @post_nolock BIT = 0

    -- Get invoice details
    SELECT @invFrght = BKAR_INV_FRGHT, @invGroup = BKAR_INV_GROUP, 
           @invLoc = LEFT(BKAR_INV_LOC, 3)
    FROM BKARINV
    WHERE BKAR_INV_NUM = @invoiceNum;

    -- If freight is zero, exit function
    IF @invFrght = 0
    BEGIN
        RETURN 0;
    END

    -- Get customer class
    SELECT @cusClass = BKAR_CLASS
    FROM BKARCUST
    WHERE BKAR_CUSTCODE = (SELECT BKAR_INV_CUSCOD FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum);

    -- Determine GL account for freight based on customer class and invoice group
    IF @cusClass = 'IC'
    BEGIN
        SET @frght_glacct = '40501     '
    END
    ELSE IF @cusClass = 'GP'
    BEGIN
        SET @frght_glacct = '40505     '
    END
    ELSE
    BEGIN
        SET @frght_glacct = '40500     '
    END

    -- If invoice group is 'CAN', set a different GL account
    IF @invGroup = 'CAN'
    BEGIN
        SET @frght_glacct = '40502     '
    END

    -- Markpoint 5 before posting
    EXEC markpoint_5_SaveToGL @invoiceNum, 0;

    -- Post to general ledger using `post_to_gl2` function
    EXEC post_to_gl2 @frght_glacct, @invLoc, 'Freight from Invoice', @invFrght, 
                     @invoiceNum, GETDATE(), 'FRGHT', NULL, 0, 'Y';

    -- Post lock check
    IF @post_nolock = 0
    BEGIN
        RETURN quit_posting(4,0);
    END

    -- Markpoint 5 after successful posting
    EXEC markpoint_5_SaveToGL @invoiceNum, 1;

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Freight Amount Check**:
   - **Condition**: The function checks if the freight amount (`BKAR_INV_FRGHT`) is non-zero. If the freight amount is `0`, the function exits without making any changes.

2. **Customer Class Lookup**:
   - **Condition**: The function retrieves the customer class (`BKAR_CLASS`) based on the customer code from the invoice.
   - **Action**: The freight GL account (`frght_glacct`) is determined based on the customer class:
     - If the customer class is `IC`, the GL account is set to `'40501'`.
     - If the customer class is `GP`, the GL account is set to `'40505'`.
     - Otherwise, the GL account is set to `'40500'`.

3. **Invoice Group Check**:
   - **Condition**: If the invoice group (`BKAR_INV_GROUP`) is `CAN`, the GL account is set to `'40502'` regardless of the customer class.

4. **Department Code Assignment**:
   - The freight department code (`BKSY_AR_FRGTDPT`) is set to the first three characters of the invoice location (`BKAR_INV_LOC`).

5. **General Ledger Posting**:
   - The function uses the `post_to_gl2` function to post the freight charges to the general ledger. The function passes the freight GL account, department, description, freight amount, invoice number, and other required details to `post_to_gl2`.

6. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function calls `quit_posting` to terminate further processing.

7. **Markpoint 5 Execution**:
   - The system executes `markpoint_5_SaveToGL` both before and after the posting action to indicate when the general ledger updates occur.

### Error Handling:
- Errors such as invalid inserts or missing required fields should raise exceptions that log the error and stop further processing.
- If the freight amount is `0`, the function returns early without posting any freight charges.

### Testing:

1. **Test Freight Posting**:
   - Create test cases where the freight amount is non-zero to ensure the function correctly posts the freight charges to the general ledger based on the customer class and invoice group.
   - Ensure that `markpoint_5_SaveToGL` is called correctly both before and after the posting.

2. **Test Freight Amount Zero**:
   - Create test cases where the freight amount is `0` to ensure the function exits without making any changes.

3. **Test Invoice Group 'CAN'**:
   - Create test cases where the invoice group is `CAN` to ensure the correct GL account (`40502`) is used for posting freight charges.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: This procedure handles the actual posting of freight charges to the general ledger. Ensure that the procedure is correctly implemented and accepts the following parameters:
  - Account
  - Department
  - Description (Freight from Invoice)
  - Total Amount (Freight)
  - Invoice Number
  - Invoice Date
  - Posting Type (`FRGHT`)
  - Customer Code (optional)
  - Lock Flag (`False`)
  - Confirmation (`Y`)

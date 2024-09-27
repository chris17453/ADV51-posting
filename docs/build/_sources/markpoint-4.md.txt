# Markpoint 4: Post to General Ledger

### Summary
This function posts the transaction to the general ledger, based on whether it is a cash transaction or an accounts receivable (non-cash) transaction. If it’s a cash transaction, the account from `BKSYCHCK` is used. For non-cash transactions, the AR account from `BKSY_AR_GLACT` is used. The `post_to_gl2` logic is used to perform the actual posting operation.

### SQL Function

```sql
CREATE PROCEDURE markpoint_4_PostToGL (
    @invoiceNum VARCHAR(20)
)
AS
BEGIN
    DECLARE @cash BIT = 0
    DECLARE @chkact VARCHAR(40)
    DECLARE @post_typ VARCHAR(3) = 'RS'
    DECLARE @post_nolock BIT = 0
    DECLARE @invTotal DECIMAL(18,2)
    DECLARE @invDate DATE
    DECLARE @cusCode VARCHAR(20)
    DECLARE @cusName VARCHAR(50)

    -- Get invoice details
    SELECT @invTotal = BKAR_INV_TOTAL, @invDate = BKAR_INV_INVDTE, 
           @cusCode = BKAR_INV_CUSCOD, @cusName = BKAR_INV_CUSNME
    FROM BKARINV
    WHERE BKAR_INV_NUM = @invoiceNum;

    -- Determine if the transaction is cash-based
    SELECT @cash = CASE WHEN BKSY_TERM_TYP IN ('C', 'A') THEN 1 ELSE 0 END
    FROM BKSYTERM
    WHERE BKSY_TERM_NUM = (SELECT BKAR_INV_TERMNM FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum);

    -- Case 1: Cash transaction
    IF @cash = 1
    BEGIN
        -- Retrieve the checking account for the transaction
        SELECT @chkact = BKSY_AR_CHKACT 
        FROM BKSYCHCK
        WHERE BKSY_CHCK_ACTNM = (SELECT BKSY_AR_CHKACT FROM BKSYTERM WHERE BKSY_TERM_NUM = (SELECT BKAR_INV_TERMNM FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum));

        -- Check if the account is valid
        IF @chkact IS NULL
        BEGIN
            RAISERROR('No valid checking account available. Cannot continue.', 16, 1)
            RETURN
        END

        -- Markpoint 4 before posting
        EXEC markpoint_4_SaveToGL @invoiceNum, 0;

        -- Post to general ledger using `post_to_gl2` logic
        EXEC post_to_gl2 @chkact, BKSY_CHCK_DPT, @cusName, @invTotal, @invoiceNum, @invDate, @post_typ, @cusCode, 0, 'Y';

        -- Post lock check
        IF @post_nolock = 0
        BEGIN
            RETURN quit_posting(3,0)
        END

        -- Markpoint 4 after successful posting
        EXEC markpoint_4_SaveToGL @invoiceNum, 1;
        
        -- Update status
        EXEC post_status;

    END
    -- Case 2: Non-cash transaction
    ELSE
    BEGIN
        -- Markpoint 4 before posting
        EXEC markpoint_4_SaveToGL @invoiceNum, 0;

        -- Post to general ledger using AR account
        EXEC post_to_gl2 BKSY_AR_GLACT, BKSY_AR_GLDPT, @cusName, @invTotal, @invoiceNum, @invDate, 'RS', @cusCode, 0, 'Y';

        -- Post lock check
        IF @post_nolock = 0
        BEGIN
            RETURN quit_posting(3,0)
        END

        -- Markpoint 4 after successful posting
        EXEC markpoint_4_SaveToGL @invoiceNum, 1;

        -- Update status
        EXEC post_status;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Cash Determination**:
   - The `cash` flag is determined by the payment term type (`BKSY_TERM_TYP`). If the term type is `C` (Cash) or `A` (Advanced), the transaction is marked as a cash transaction (`cash = 1`).

2. **Cash Transaction Handling**:
   - For cash transactions, the checking account (`BKSY_AR_CHKACT`) is retrieved from the `BKSYCHCK` table. 
   - The transaction is posted to the general ledger using the `post_to_gl2` function with the account and department (`BKSY_CHCK_ACT` and `BKSY_CHCK_DPT`).
   - Markpoint 4 is executed before and after the posting to track the transaction state.

3. **Non-Cash Transaction Handling**:
   - For non-cash transactions, the AR account (`BKSY_AR_GLACT`) is used.
   - The transaction is posted to the general ledger using the `post_to_gl2` function with the account and department (`BKSY_AR_GLACT` and `BKSY_AR_GLDPT`).
   - Markpoint 4 is executed before and after the posting to track the transaction state.

4. **Lock Handling**:
   - If the `post_nolock` flag is not set (i.e., `post_nolock = 0`), the function terminates by calling `quit_posting` to ensure no further processing happens.
   
5. **Markpoint 4 Execution**:
   - The system executes `markpoint_4_SaveToGL` both before and after the posting action to indicate when the general ledger updates occur.

6. **Post Status**:
   - After a successful post, the function calls `post_status` to ensure all statuses are updated correctly.

### Error Handling:
- If no valid checking account is found for cash transactions, an error is raised with the message:
  - *"No valid checking account available. Cannot continue."*
- Errors such as invalid inserts or missing required fields should raise exceptions that log the error and stop further processing.

### Testing:

1. **Test Cash Transactions**:
   - Create test cases with payment term types `C` or `A` to ensure cash transactions are correctly posted to the general ledger using the `BKSY_AR_CHKACT` account.
   - Ensure that `markpoint_4_SaveToGL` is called correctly both before and after the posting.

2. **Test Non-Cash Transactions**:
   - Create test cases with non-cash payment term types to ensure non-cash transactions are posted to the general ledger using the `BKSY_AR_GLACT` account.
   - Ensure that `markpoint_4_SaveToGL` is called correctly both before and after the posting.

3. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: This procedure handles the actual posting of transactions to the general ledger. Ensure that the procedure is correctly implemented and accepts the following parameters:
  - Account
  - Department
  - Customer Name
  - Total Amount
  - Invoice Number
  - Invoice Date
  - Posting Type
  - Customer Code
  - Lock Flag (`False`)
  - Confirmation (`Y`)

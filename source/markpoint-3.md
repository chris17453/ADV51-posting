# Markpoint 3: Save to Accounts Receivable and Check Account Register

### Summary
This function updates the Accounts Receivable statements (`BKARINVT`) or the Check Account Register (`BKGLCHK`), based on whether the transaction is cash-based or not. It determines the cash status by looking at the payment term type and uses the `ent_chckact` logic to retrieve the appropriate checking account based on `BKSY_AR_CHKACT`.

### SQL Function

```sql
CREATE PROCEDURE markpoint_3_SaveToARAndCheckAccount (
    @invoiceNum VARCHAR(20)
)
AS
BEGIN
    DECLARE @cash BIT = 0
    DECLARE @post_typ VARCHAR(3) = 'RS'
    DECLARE @invTotal DECIMAL(18,2)
    DECLARE @invDate DATE
    DECLARE @invTermName VARCHAR(50)
    DECLARE @invTermType CHAR(1)
    DECLARE @invDesc VARCHAR(50)
    DECLARE @cusName VARCHAR(50)
    DECLARE @slsp VARCHAR(20)
    DECLARE @webID VARCHAR(20)
    DECLARE @cusCode VARCHAR(20)
    DECLARE @chkact VARCHAR(40)
    DECLARE @chosenAct VARCHAR(40)

    -- Get invoice details
    SELECT @invTotal = BKAR_INV_TOTAL, @invDate = BKAR_INV_INVDTE, @invTermName = BKAR_INV_TERMNM, 
           @invDesc = BKAR_INV_DESC, @cusName = BKAR_INV_CUSNME, @slsp = BKAR_INV_SLSP, 
           @webID = BKAR_INV_WEBID, @cusCode = BKAR_INV_CUSCOD
    FROM BKARINV
    WHERE BKAR_INV_NUM = @invoiceNum;

    -- Determine if the transaction is cash-based
    IF @invTermName IS NOT NULL
    BEGIN
        SELECT @invTermType = BKSY_TERM_TYP 
        FROM BKSYTERM 
        WHERE BKSY_TERM_NUM = @invTermName;

        IF @invTermType IN ('C', 'A') 
        BEGIN
            SET @cash = 1;
            SET @post_typ = 'CR';
            IF @invTotal < 0
            BEGIN
                SET @post_typ = 'CD';
            END
        END
    END

    -- If not a cash transaction, update BKARINVT (A/R statements)
    IF @cash = 0
    BEGIN
        -- Populate BKARINVT with the relevant data
        INSERT INTO BKARINVT (BKAR_INVT_NUM, BKAR_INVT_DATE, BKAR_INVT_CODE, BKAR_INVT_AMT, 
                              BKAR_INVT_AMTRM, BKAR_INVT_DESC, BKAR_INVT_TYPE, BKAR_INVT_TERMN, 
                              BKAR_INVT_SLSP, BKAR_INVT_WEBID)
        VALUES (@invoiceNum, @invDate, @cusCode, @invTotal, @invTotal, 
                CASE 
                    WHEN LEFT(@invDesc, 5) = 'RMA #' THEN CONCAT('RMA#', SUBSTRING(@invDesc, 6, 30))
                    WHEN @invDesc = '' AND @invTotal < 0 THEN 'Credit Invoice'
                    WHEN @invDesc = '' THEN 'Invoice'
                    ELSE @invDesc
                END,
                CASE 
                    WHEN @invTotal < 0 THEN 'C' 
                    ELSE 'I' 
                END,
                @invTermName, @slsp, @webID);

        -- Markpoint 3 for BKARINVT
        EXEC markpoint_3_SaveToARStatement @invoiceNum;

    END
    ELSE
    BEGIN
        -- Step 1: Use BKSY_AR_CHKACT for account selection
        SELECT @chkact = BKSY_AR_CHKACT 
        FROM BKSYTERM
        WHERE BKSY_TERM_NUM = @invTermName;

        -- Step 2: Ensure a valid account is selected from BKSYCHCK based on BKSY_AR_CHKACT
        SET @chosenAct = (
            SELECT BKSY_CHCK_ACTNM 
            FROM BKSYCHCK
            WHERE BKSY_CHCK_ACTNM = @chkact
              AND BKSY_CHCK_NAME <> ''   -- Valid account names
              AND BKSY_CHCK_ACTIV <> 'N' -- Only active accounts
        )

        -- If no valid checking account found, raise an error
        IF @chosenAct IS NULL
        BEGIN
            RAISERROR('No valid checking account available. Cannot continue.', 16, 1)
            RETURN
        END

        -- Step 3: Insert into BKGLCHK (Check Account Register)
        INSERT INTO BKGLCHK (BKGL_CHK_AMT, BKGL_CHK_DATE, BKGL_CHK_TYPE, BKGL_CHK_NUM, 
                             BKGL_CHK_NAME, BKGL_CHK_FLAG, BKGL_CHK_CHKACT)
        VALUES (@invTotal, @invDate, 
                CASE 
                    WHEN @invTotal < 0 THEN 'C' 
                    ELSE 'D' 
                END, 
                @invoiceNum, @cusName, '', @chosenAct);

        -- Markpoint 3 for BKGLCHK
        EXEC markpoint_3_SaveToCheckAccount @invoiceNum;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Cash Determination**:
   - The `cash` flag is set to `True` if the payment term type (`BKSY_TERM_TYP`) associated with the invoice is either `C` (Cash) or `A` (Advanced). 
   - The `post_typ` is set to:
     - `CR` for cash receipts.
     - `CD` for cash debits if the invoice total is negative.

2. **Accounts Receivable Update (Non-Cash Transactions)**:
   - **Condition**: If the transaction is non-cash (`cash = 0`), insert the relevant details into the `BKARINVT` table.
   - The invoice description is updated based on whether the description starts with "RMA #", or if it's a credit invoice.

3. **Check Account Register Update (Cash Transactions)**:
   - **Condition**: If the transaction is cash-based (`cash = 1`), retrieve the correct checking account using `BKSY_AR_CHKACT` from `BKSYTERM`.
   - **Action**: The selected account (`BKSY_AR_CHKACT`) must exist in `BKSYCHCK` and must be active. If a valid account is found, the transaction details are inserted into the `BKGLCHK` table (Check Account Register).
   - The type is set to `C` for credits or `D` for debits.
   - If no valid checking account is found, the function raises an error and halts further execution.

4. **Markpoint 3 Execution**:
   - After inserting the data, the system calls the appropriate `markpoint_3_SaveToARStatement` or `markpoint_3_SaveToCheckAccount` procedure depending on whether the transaction was non-cash or cash-based.

### Error Handling:
- If no valid checking account is found when handling cash transactions (based on `BKSY_AR_CHKACT`), an error is raised with the message:
  - *"No valid checking account available. Cannot continue."*
- Errors such as invalid inserts or missing required fields should raise exceptions that log the error and stop further processing.

### Testing:
1. **Test Non-Cash Transactions**:
   - Create test cases where the payment term type is not `C` or `A`, and verify that the `BKARINVT` table is updated with correct details and the appropriate invoice description (`RMA`, `Invoice`, or `Credit Invoice`).
   - Ensure that `markpoint_3_SaveToARStatement` is called correctly.

2. **Test Cash Transactions**:
   - Create test cases with payment term types `C` or `A` to ensure cash transactions are correctly inserted into the `BKGLCHK` table with correct flags and amounts.
   - Ensure that `markpoint_3_SaveToCheckAccount` is called correctly.

3. **Negative Totals**:
   - Ensure that credit handling for both cash and non-cash transactions works properly and the correct `post_typ` (`CR`, `CD`) is assigned.

4. **Checking Account Selection**:
   - Test the account selection process based on the `BKSY_AR_CHKACT` field. Ensure it retrieves the correct account and validates its existence in the `BKSYCHCK` table. If no account is found or is inactive, confirm that the function correctly raises an error.

### Notes:
- The checking account is selected based on the `BKSY_AR_CHKACT` field in `BKSYTERM`. The function checks for the existence of the specified account in the `BKSYCHCK` table and ensures it is active. If no valid account is found, the process is halted with an error message.
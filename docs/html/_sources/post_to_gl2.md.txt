# post_to_gl2: Post to General Ledger

## Summary:
This function posts financial data to the general ledger (GL) based on the provided account, department, description, amount, and other details. It checks if the GL account exists, falls back to a clearing account if needed, manages cash transaction logic, and updates the general ledger records.

## MSSQL Procedure

```sql
CREATE PROCEDURE PostToGL2
    @post_acct VARCHAR(15),
    @post_dpt VARCHAR(10),
    @post_desc VARCHAR(100),
    @post_amt FLOAT,
    @post_invnum VARCHAR(15),
    @post_date DATE,
    @post_tran_type VARCHAR(10),
    @post_code VARCHAR(5),
    @post_chk_cash BIT,
    @post_quit BIT OUT
AS
BEGIN
    -- Declare variables
    DECLARE @post_mnth INT;
    DECLARE @BKGL_ACCT VARCHAR(15);
    DECLARE @BKGL_GLDPT VARCHAR(10);
    DECLARE @post_other BIT = 0;
    DECLARE @post_fail BIT = 0;
    DECLARE @post_amt_abs FLOAT;
    DECLARE @BKGL_TRN_DC CHAR(1);

    SET @post_quit = 0;

    -- If post amount is zero, exit early
    IF @post_amt = 0 RETURN;

    -- Calculate posting month
    SET @post_mnth = MONTH(@post_date) + 1;

    -- Initialize GL account and department
    SET @BKGL_ACCT = @post_acct;
    SET @BKGL_GLDPT = @post_dpt;

    -- Check if the GL account exists (BKGLCOA table)
    IF NOT EXISTS (SELECT 1 FROM BKGLCOA WHERE BKGL_ACCT = @post_acct AND BKGL_GLDPT = @post_dpt)
    BEGIN
        -- Use the clearing account if the original account is not found
        SET @post_other = 1;
        SELECT @BKGL_ACCT = BKSY_GL_CLRING, @BKGL_GLDPT = BKSY_GLDPT_CLR;

        -- Check if clearing account exists
        IF NOT EXISTS (SELECT 1 FROM BKGLCOA WHERE BKGL_ACCT = @BKGL_ACCT AND BKGL_GLDPT = @BKGL_GLDPT)
        BEGIN
            -- Fail if neither the original nor the clearing account is found
            SET @post_fail = 1;
            SET @post_quit = 1;
            RETURN;
        END
    END

    -- Set transaction direction (debit/credit) based on the amount
    SET @BKGL_TRN_DC = 'D';
    IF @post_amt < 0
    BEGIN
        SET @BKGL_TRN_DC = 'C';
    END

    -- Post transaction details into BKGLTRAN table
    INSERT INTO BKGLTRAN (BKGL_TRN_TYPE, BKGL_TRN_DATE, BKGL_TRN_INVC, BKGL_TRN_DESC, BKGL_TRN_GLACCT, BKGL_TRN_GLDPT, BKGL_TRN_CODE, BKGL_TRN_DC, BKGL_TRN_AMT)
    VALUES (@post_tran_type, @post_date, @post_invnum, @post_desc, @BKGL_ACCT, @BKGL_GLDPT, @post_code, @BKGL_TRN_DC, ABS(@post_amt));

    -- Handle cash transaction if required
    IF @post_chk_cash = 1
    BEGIN
        -- Check if the cash account exists in BKSYCHCK table
        IF EXISTS (SELECT 1 FROM BKSYCHCK WHERE BKSY_CHCK_ACT = @BKGL_ACCT AND BKSY_CHCK_GLDPT = @BKGL_GLDPT)
        BEGIN
            -- Insert cash transaction details into BKGLCHK table
            INSERT INTO BKGLCHK (BKGL_CHK_ACTNM, BKGL_CHK_DATE, BKGL_CHK_TYPE, BKGL_CHK_AMT, BKGL_CHK_NUM, BKGL_CHK_NAME, BKGL_CHK_FLAG)
            VALUES (@BKGL_ACCT, @post_date, 
                    CASE WHEN @post_amt < 0 THEN 'C' ELSE 'D' END, 
                    ABS(@post_amt), @post_invnum, @post_desc, '');
        END
    END

    -- Update BKGLCOA balances based on the posting month and year
    IF YEAR(@post_date) = YEAR(GETDATE())
    BEGIN
        UPDATE BKGLCOA
        SET BKGL_CURRENT[@post_mnth] = BKGL_CURRENT[@post_mnth] + @post_amt
        WHERE BKGL_ACCT = @BKGL_ACCT AND BKGL_GLDPT = @BKGL_GLDPT;
    END
    ELSE
    BEGIN
        UPDATE BKGLCOA
        SET BKGL_1YPAST[@post_mnth] = BKGL_1YPAST[@post_mnth] + @post_amt
        WHERE BKGL_ACCT = @BKGL_ACCT AND BKGL_GLDPT = @BKGL_GLDPT;
    END

    -- Recalculate total balance (sum of months)
    DECLARE @current_total FLOAT = 0;
    DECLARE @i INT = 1;

    WHILE @i <= 13
    BEGIN
        SET @current_total = @current_total + (SELECT BKGL_CURRENT[@i] FROM BKGLCOA WHERE BKGL_ACCT = @BKGL_ACCT AND BKGL_GLDPT = @BKGL_GLDPT);
        SET @i = @i + 1;
    END

    -- Update the total balance for the account
    UPDATE BKGLCOA
    SET BKGL_CURRENT[14] = @current_total
    WHERE BKGL_ACCT = @BKGL_ACCT AND BKGL_GLDPT = @BKGL_GLDPT;

END
GO
```

### Breakdown of Tasks:

1. **Check for Zero Amount:**
   - The function exits early if `@post_amt = 0`.

2. **Calculate Posting Month:**
   - Adds 1 to the month extracted from `@post_date` to determine the posting month.

3. **Validate GL Account:**
   - Checks if the GL account and department exist in the `BKGLCOA` table. If not found, it falls back to a clearing account (`BKSY_GL_CLRING`).
   - If neither the original nor clearing account is found, the function sets `@post_quit = 1` and returns early.

4. **Set Debit or Credit Based on Amount:**
   - The function sets the transaction as a debit (`D`) or credit (`C`) depending on whether the amount is positive or negative.

5. **Insert Transaction into GL Table:**
   - Inserts the transaction details into the `BKGLTRAN` table, with values for account, department, description, transaction type, code, and the debit/credit flag.

6. **Cash Transaction Handling:**
   - If the transaction is a cash transaction (`@post_chk_cash = 1`), it checks the `BKSYCHCK` table for a cash account.
   - If found, the function inserts a record into the `BKGLCHK` table with the cash details.

7. **Update GL Account Balances:**
   - Depending on whether the transaction occurred in the current year or a past year, it updates either `BKGL_CURRENT` or `BKGL_1YPAST` fields for the specific posting month.

8. **Recalculate Total Balances:**
   - Recalculates the total balance by summing the balances from months 1 to 13, and then updates the total balance (`BKGL_CURRENT[14]`) for the account.

### Error Handling:

- Proper error handling should be included with `TRY...CATCH` blocks to ensure that any errors during the `INSERT`, `UPDATE`, or validation processes are managed.
- If the GL account cannot be found (original or clearing), the function gracefully exits by setting `@post_quit = 1`.

### Testing:

- **Test Case 1: Valid Posting**
  - Run the function with valid data (account, department, amount) and verify that the general ledger transaction is recorded correctly.
  
- **Test Case 2: Missing Account**
  - Run the function with a missing or invalid account and confirm that it falls back to the clearing account or exits if neither account is found.

- **Test Case 3: Cash Transaction**
  - Run the function with `@post_chk_cash = 1` and verify that a record is correctly inserted into the `BKGLCHK` table for a cash transaction.

- **Test Case 4: Error Handling**
  - Simulate database constraints or other errors to ensure that the function gracefully handles failures without leaving incomplete transactions.

### Notes:

- **Locking and Concurrency**: The function assumes appropriate row-level locking during the `SELECT`, `INSERT`, and `UPDATE` operations to ensure data integrity.
- **Performance Considerations**: The recalculation of total balances is done by summing each month's balance, which could impact performance on larger datasets. If performance becomes an issue, consider indexing and optimizing the queries.
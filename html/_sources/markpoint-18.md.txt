# Markpoint 18: Update Points History

## Summary:
This function updates the points history for a customer when the points earned are not zero, the invoice group is not "CRD," and the `lucky7` flag is not set to "N." It sets mark point 18 to track the operation and inserts the relevant transaction details into the `BKPTSHST` table, ensuring that it is only performed once.

## MSSQL Function

```sql
CREATE PROCEDURE Markpoint18_UpdatePointsHistory
    @invoice_number VARCHAR(15),
    @points_cust VARCHAR(20),
    @points_class VARCHAR(10),
    @points_rate FLOAT,
    @points_earned FLOAT,
    @tot_ext FLOAT,
    @lucky7 CHAR(1)
AS
BEGIN
    -- Declare variables
    DECLARE @inv_group VARCHAR(3), @inv_date DATE, @inv_desc VARCHAR(100), @inv_num VARCHAR(15);

    -- Retrieve necessary invoice details
    SELECT @inv_group = BKAR_INV_GROUP, @inv_date = BKAR_INV_INVDTE, 
           @inv_desc = BKAR_INV_DESC, @inv_num = BKAR_INV_NUM
    FROM BKAR_INV
    WHERE BKAR_INV_INVNUM = @invoice_number;

    -- If points_earned is 0, invoice group is not "CRD", and lucky7 is not "N", process
    IF @points_earned != 0 AND @inv_group != 'CRD' AND @lucky7 != 'N'
    BEGIN
        -- Check if mark point 19 is already processed
        IF NOT EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK = 19)
        BEGIN
            -- Find the customer points record
            SELECT BKAR_PR_CSTCOD
            FROM BKARPR
            WHERE BKAR_PR_CSTCOD = @points_cust;
        END

        -- Check if mark point 18 is already processed
        IF NOT EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK = 18)
        BEGIN
            -- Set points history details
            DECLARE @current_time TIME = GETDATE();

            -- Insert into points history table
            INSERT INTO BKPTSHST (BKPTSHST_CUST, BKPTSHST_CLASS, BKPTSHST_RATE, BKPTSHST_DATE, BKPTSHST_TIME, 
                                  BKPTSHST_TRNSNM, BKPTSHST_DESC, BKPTSHST_POINTS, BKPTSHST_AMOUNT)
            VALUES (@points_cust, @points_class, @points_rate, @inv_date, @current_time, 
                    @inv_num, @inv_desc, @points_earned, @tot_ext);

            -- Set mark point 18 (start)
            EXEC mark_point 18, 0, False;

            -- Save the record (implicitly done by the INSERT command in SQL)

            -- Complete mark point 18
            EXEC mark_point 18, 0, True;
        END
    END
END
GO
```

### Breakdown of Tasks:

1. **Check Conditions:**
   - The function checks if `points_earned != 0`, `BKAR_INV_GROUP != 'CRD'`, and `lucky7 != 'N'`. If any of these conditions are false, the function exits early.

2. **Check Markpoint 19:**
   - The function checks if mark point 19 has been processed already. If not, it retrieves the customer points record from the `BKARPR` table.

3. **Set Points History (Markpoint 18):**
   - If mark point 18 has not been processed, it sets the details for the points history (`BKPTSHST`) and inserts a new record for the transaction into the `BKPTSHST` table.

4. **Set and Complete Markpoint 18:**
   - The `mark_point` function is used to set the mark point 18 at the beginning of the operation and complete it once the record has been successfully inserted.

### Error Handling:

- The function should include `TRY...CATCH` blocks to ensure that any errors during the insert operation are handled properly.
- If an error occurs during the points history update, appropriate rollback or cleanup should be performed.

### Testing:

- **Test Case 1: Valid Points Update**
  - Run the function with valid data, where `points_earned != 0`, and ensure the points history is correctly updated and mark point 18 is set and completed.

- **Test Case 2: No Points Earned**
  - Run the function with `points_earned = 0` and verify that no update is performed, and mark point 18 is not set.

- **Test Case 3: Error Handling**
  - Introduce invalid data (e.g., non-existent customer) and ensure the function handles the error gracefully without affecting the rest of the system.

### Notes:

- **Mark Points 18 and 19**: The function uses mark points 18 and 19 to control the flow of processing and ensure that the operations are only performed once for the specific transaction.
- **Performance Considerations**: The `INSERT` and `SELECT` operations are lightweight, but additional logic might be added to handle concurrent transactions or large datasets.
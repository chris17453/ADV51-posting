# Markpoint 19: Update Customer Points

## Summary:
This function updates the customer points (`BKAR_PR_POINTS`) by adding the `points_earned` to the existing points if the conditions are met: `points_earned != 0`, `BKAR_INV_GROUP != 'CRD'`, and `lucky7 != 'N'`. It uses `mark_point` 19 to track the operation, ensuring it is only performed once.

## MSSQL Function

```sql
CREATE PROCEDURE Markpoint19_UpdateCustomerPoints
    @invoice_number VARCHAR(15), 
    @points_earned FLOAT,
    @points_cust VARCHAR(20),
    @lucky7 CHAR(1)
AS
BEGIN
    -- Declare variables
    DECLARE @inv_group VARCHAR(3), @current_points FLOAT;

    -- Retrieve the necessary invoice details
    SELECT @inv_group = BKAR_INV_GROUP
    FROM BKAR_INV
    WHERE BKAR_INV_INVNUM = @invoice_number;

    -- Check the conditions: points_earned != 0, invoice group is not 'CRD', and lucky7 is not 'N'
    IF @points_earned != 0 AND @inv_group != 'CRD' AND @lucky7 != 'N'
    BEGIN
        -- Retrieve the customer points record from BKARPR based on the customer code
        SELECT @current_points = BKAR_PR_POINTS
        FROM BKARPR
        WHERE BKAR_PR_CSTCOD = @points_cust;

        -- Check if mark point 19 has not already been processed
        IF NOT EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK = 19)
        BEGIN
            -- Update customer points by adding the points earned
            SET @current_points = @current_points + @points_earned;

            -- Set mark point 19 (start of the operation)
            EXEC mark_point 19, 0, False;

            -- Update the BKAR_PR_POINTS field
            UPDATE BKARPR
            SET BKAR_PR_POINTS = @current_points
            WHERE BKAR_PR_CSTCOD = @points_cust;

            -- Complete mark point 19
            EXEC mark_point 19, 0, True;
        END
    END
END
GO
```

### Breakdown of Tasks:

1. **Retrieve Invoice and Customer Data:**
   - The function retrieves the `BKAR_INV_GROUP` field from the `BKAR_INV` table based on the provided `@invoice_number`.
   - It retrieves the current points from the `BKARPR` table using the customer code (`@points_cust`).

2. **Check Conditions:**
   - The function ensures that the following conditions are met:
     - `points_earned != 0`
     - `BKAR_INV_GROUP != 'CRD'`
     - `lucky7 != 'N'`
   - If any of these conditions are false, the function exits early.

3. **Check Markpoint 19:**
   - The function checks if mark point 19 has already been processed using a query on the `BKSOMARK` table. If it has, the function exits early.

4. **Update Points:**
   - If mark point 19 has not been processed, it adds the `points_earned` to the existing points and updates the `BKAR_PR_POINTS` field in the `BKARPR` table.

5. **Set and Complete Markpoint 19:**
   - The `mark_point` function is used to track the beginning and completion of the update operation for mark point 19.

### Error Handling:

- Proper error handling should be included using `TRY...CATCH` blocks to ensure that any issues during the `UPDATE` or `mark_point` processes are handled properly.
- If an error occurs during the points update, appropriate rollback or cleanup should be performed.

### Testing:

- **Test Case 1: Valid Points Update**
  - Run the function with valid data, where `points_earned != 0`, and verify that the `BKAR_PR_POINTS` field is updated correctly and mark point 19 is set and completed.

- **Test Case 2: No Points Earned**
  - Run the function with `points_earned = 0` and ensure that no update is performed and mark point 19 is not set.

- **Test Case 3: Error Handling**
  - Introduce invalid data (e.g., a non-existent customer) and verify that the function handles the error gracefully without affecting the rest of the system.

### Notes:

- **Mark Point Usage:** The function uses mark point 19 to track the beginning and end of the update operation, ensuring that it is only performed once for the specific transaction.
- **Performance Considerations:** This operation involves a simple `SELECT` and `UPDATE`, so it is lightweight. However, you may want to test with larger datasets to ensure the performance holds up in production scenarios.
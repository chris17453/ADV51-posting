# Markpoint 24: Process Invoice and Update Sales

## Summary:
This function processes an invoice by updating its status, handling sales records, and processing return merchandise authorization (RMA) records based on mark point 24. The `invoice_group` is derived from the first two characters of `BKAR_INV_GROUP`. The function uses the `mark_point` SQL function to set the appropriate mark point during the process.

## MSSQL Function

```sql
CREATE PROCEDURE Markpoint24_ProcessInvoiceAndUpdateSales
    @invoice_number VARCHAR(15)
AS
BEGIN
    -- Declare variables
    DECLARE @invoice_group VARCHAR(2), @inv_subtotal FLOAT, @inv_act_date DATE, @rma_num VARCHAR(20), 
            @slsp_num INT, @rma_status CHAR(1), @inv_custcode VARCHAR(20), @inv_shipcode VARCHAR(20), 
            @inv_date DATE, @mark INT, @sales_bucket_amt FLOAT;

    -- Set invoice processed indicator and update activity date
    UPDATE BKAR_INV
    SET BKAR_INV_INVCD = 'Y',
        BKAR_INV_ACTDTE = GETDATE()
    WHERE BKAR_INV_INVNUM = @invoice_number;

    -- Retrieve necessary invoice details 
    SELECT @invoice_group = LEFT(BKAR_INV_GROUP, 2), -- Extract first 2 characters
           @inv_subtotal = BKAR_INV_SUBTOT, 
           @inv_date = BKAR_INV_INVDTE, 
           @inv_custcode = BKAR_INV_CUSCOD, 
           @inv_shipcode = BKAR_INV_SHPCOD
    FROM BKAR_INV
    WHERE BKAR_INV_INVNUM = @invoice_number;

    -- Check for non-credit invoices and update sales bucket (Markpoint 24)
    IF @invoice_group != 'CR'
    BEGIN
        -- Set the mark point to 24
        EXEC mark_point 24, 0, False;

        -- Check if sales bucket record exists
        IF EXISTS (SELECT 1 FROM BKSOBUCK WHERE BKSO_BUCK_CUST = @inv_custcode AND 
                   BKSO_BUCK_MONTH = MONTH(@inv_date) AND BKSO_BUCK_YEAR = YEAR(@inv_date))
        BEGIN
            -- Update sales bucket
            UPDATE BKSOBUCK
            SET BKSO_BUCK_AMT = BKSO_BUCK_AMT + @inv_subtotal
            WHERE BKSO_BUCK_CUST = @inv_custcode AND 
                  BKSO_BUCK_MONTH = MONTH(@inv_date) AND BKSO_BUCK_YEAR = YEAR(@inv_date);
        END
        ELSE
        BEGIN
            -- Insert new sales bucket record
            INSERT INTO BKSOBUCK (BKSO_BUCK_CUST, BKSO_BUCK_MONTH, BKSO_BUCK_YEAR, BKSO_BUCK_AMT)
            VALUES (@inv_custcode, MONTH(@inv_date), YEAR(@inv_date), @inv_subtotal);
        END
        
        -- Set the mark point to complete for 24
        EXEC mark_point 24, 0, True;
    END

    -- Process RMA if the invoice group is 'RM'
    IF @invoice_group = 'RM'
    BEGIN
        DECLARE curRMA CURSOR FOR
        SELECT BKICLWTR_RMANUM, BKICLWTR_STATUS
        FROM BKICLWTR
        WHERE BKICLWTR_RMANUM = (SELECT BKRMA_H_RMANUM FROM BKRMA_H WHERE BKRMA_H_INVNUM = @invoice_number)
          AND BKICLWTR_STATUS = '';

        OPEN curRMA;
        FETCH NEXT FROM curRMA INTO @rma_num, @rma_status;

        WHILE @@FETCH_STATUS = 0
        BEGIN
            IF @invoice_group = 'RMS'
            BEGIN
                UPDATE BKICLWTR
                SET BKICLWTR_STATUS = 'X', BKICLWTR_XDATE = @inv_date, BKICLWTR_DATE = @inv_date
                WHERE BKICLWTR_RMANUM = @rma_num;
            END
            ELSE
            BEGIN
                UPDATE BKICLWTR
                SET BKICLWTR_STATUS = 'P', BKICLWTR_DATE = @inv_date
                WHERE BKICLWTR_RMANUM = @rma_num;
            END

            FETCH NEXT FROM curRMA INTO @rma_num, @rma_status;
        END

        CLOSE curRMA;
        DEALLOCATE curRMA;
    END

    -- Log invoice to history (BKARHINV)
    INSERT INTO BKARHINV (FILEDESC, RECS_SAVED, ROW)
    VALUES ('BKARHINV - History header', 1, 1);  -- Adjust RECS_SAVED and ROW accordingly

END
GO
```

### Breakdown of Tasks:

1. **Set Invoice Processed Indicator:**
   - Updates the `BKAR_INV` table to set `BKAR_INV_INVCD = 'Y'` and the current date for `BKAR_INV_ACTDTE`.

2. **Sales Bucket Update:**
   - If the invoice group (first two characters of `BKAR_INV_GROUP`) is not 'CR', the sales bucket (`BKSOBUCK`) is updated based on the customer code and invoice date. The `mark_point` function is used to set and complete the mark point (24).

3. **Process RMA (Return Merchandise Authorization):**
   - If the invoice group (first two characters) is 'RM', process related `BKICLWTR` records, updating the status and dates accordingly.

4. **Log Invoice to History:**
   - Insert a record into `BKARHINV` to log the invoice as processed.

### Error Handling:

- Use `TRY...CATCH` blocks where necessary for handling unexpected errors, especially in transaction-heavy sections like `RMA` updates.
- Ensure that no records are processed if key fields (like customer code or sales rep code) are missing or invalid.

### Testing:

- **Test Case 1: Standard Invoice**
  - Run the function with a standard invoice. Verify that the invoice status is updated, and relevant sales records are updated accordingly.
  
- **Test Case 2: RMA Invoice**
  - Run the function with an 'RM' group invoice. Ensure the `BKICLWTR` table is updated based on the conditions for the 'RM' group.
  
- **Test Case 3: Markpoint Handling**
  - Run the function and ensure the `mark_point` function sets and completes the mark point 24 as expected.

- **Test Case 4: Error Handling**
  - Introduce missing records or invalid data and verify that the error handling responds correctly without crashing the system.

### Notes:

- **Record Locking:** Ensure that any records being updated are locked during the operation to avoid concurrency issues.
- **Performance Considerations:** Test the function with large datasets to ensure performance does not degrade, particularly with the cursor used for processing `BKICLWTR` records.
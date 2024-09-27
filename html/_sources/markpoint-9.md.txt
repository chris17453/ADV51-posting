# Markpoint 9: Update Inventory Master

### Summary
This function updates the last sale date (`lsale`) in the inventory master (`BKICMSTR`) if the invoice date is more recent than the current last sale date for the product. The function skips updating certain products like "ANTIFREEZE". The update is performed conditionally, locking the record if possible, and saving changes only if necessary.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_9_UpdateInventoryMaster (
    @invoiceNum VARCHAR(20),
    @lineNum INT
)
AS
BEGIN
    DECLARE @prodCode VARCHAR(20)
    DECLARE @invDate DATE
    DECLARE @lastSale DATE
    DECLARE @skipUpdate BIT = 0
    DECLARE @passMark INT = 9

    -- Get product code and invoice date from invoice line
    SELECT @prodCode = BKAR_INVL_PCODE, @invDate = BKAR_INV_INVDTE
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Skip update if product is 'ANTIFREEZE'
    IF @prodCode = 'ANTIFREEZE'
    BEGIN
        SET @skipUpdate = 1;
    END

    -- Continue only if product is not 'ANTIFREEZE'
    IF @skipUpdate = 0
    BEGIN
        -- Get the last sale date from inventory master
        SELECT @lastSale = BKIC_PROD_LSALE
        FROM BKICMSTR
        WHERE BKIC_PROD_CODE = @prodCode;

        -- Update the last sale date if the invoice date is more recent
        IF @invDate > @lastSale
        BEGIN
            -- Markpoint 9 before saving changes
            EXEC markpoint_9_SaveToInventoryMaster @invoiceNum, @lineNum, 0;

            -- Lock the inventory master record (optional, not critical)
            BEGIN TRY
                -- Lock the record
                SELECT * 
                FROM BKICMSTR WITH (ROWLOCK, HOLDLOCK)
                WHERE BKIC_PROD_CODE = @prodCode;

                -- Update the last sale date
                UPDATE BKICMSTR
                SET BKIC_PROD_LSALE = @invDate
                WHERE BKIC_PROD_CODE = @prodCode;

                -- Markpoint 9 after saving changes
                EXEC markpoint_9_SaveToInventoryMaster @invoiceNum, @lineNum, 1;
            END TRY
            BEGIN CATCH
                -- Handle lock error (prod_lock_err)
                RAISERROR('Unable to lock the product record.', 16, 1);
                RETURN;
            END CATCH
        END
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Product Code and Invoice Date Lookup**:
   - The function retrieves the product code (`BKAR_INVL_PCODE`) and invoice date (`BKAR_INV_INVDTE`) from the invoice line (`BKARINVL`).

2. **Product Exclusion**:
   - **Condition**: The function skips updating the last sale date for the product "ANTIFREEZE" by checking the product code.
   - If the product is "ANTIFREEZE", the function sets a flag to skip the update and exits early without making changes.

3. **Inventory Master Lookup**:
   - The function retrieves the last sale date (`BKIC_PROD_LSALE`) from the inventory master (`BKICMSTR`).

4. **Last Sale Date Update**:
   - **Condition**: If the invoice date is more recent than the current last sale date, the function proceeds to update the last sale date in `BKICMSTR`.

5. **Lock Handling**:
   - **Action**: The function attempts to lock the inventory master record for the product using a row-level lock (`ROWLOCK, HOLDLOCK`). This step is optional but ensures no other processes can modify the record during the update.

6. **Markpoint 9 Execution**:
   - The system executes `markpoint_9_SaveToInventoryMaster` both before and after saving changes to the inventory master.

7. **Error Handling**:
   - If the record lock fails, the function raises an error and exits, skipping the update.

### Error Handling:
- **Lock Failure**: If the inventory master record cannot be locked, the function raises an error with the message: *"Unable to lock the product record."*
- **Product Exclusion**: If the product is "ANTIFREEZE", the function exits early without making any updates.

### Testing:

1. **Test Update for Regular Products**:
   - Create test cases where the product is not "ANTIFREEZE" and the invoice date is more recent than the last sale date. Ensure that the function updates the last sale date in `BKICMSTR` correctly.

2. **Test Exclusion for 'ANTIFREEZE'**:
   - Create test cases where the product is "ANTIFREEZE". Ensure that the function skips updating the last sale date and exits early.

3. **Test Lock Handling**:
   - Create test cases where the inventory master record is locked by another process. Ensure that the function handles the lock error and exits without making changes.

4. **Test Post Lock Handling**:
   - Test scenarios where the function attempts to lock the record and ensure it handles the `ROWLOCK, HOLDLOCK` logic correctly.

### Notes:
- **Post to Inventory Master**: The update to `BKICMSTR` is only made if the invoice date is more recent than the last sale date, and the product is not "ANTIFREEZE".
- The locking mechanism (`ROWLOCK, HOLDLOCK`) ensures data consistency, though it is marked as optional and not critical.
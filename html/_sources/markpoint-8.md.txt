# Markpoint 8: Save to Inventory Warehouse (RMA)

### Summary
This function handles adjustments for warehouse inventory location (`BKICLOCW`) in the case of RMA (return merchandise authorization) transactions. It updates the quantity on hand (`UOH`) and recalculates the average cost (`AVGC`) for the warehouse location. The logic is only applied if the return involves an auto-backorder flag (`BKAR_INVL_AUTOB = 'W'`).
- This is a PER (RMA) INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_8_SaveToWarehouse (
    @invoiceNum VARCHAR(20),
    @lineNum INT
)
AS
BEGIN
    DECLARE @prodCode VARCHAR(20)
    DECLARE @locCode VARCHAR(10)
    DECLARE @pqty DECIMAL(18,2)
    DECLARE @locUOH DECIMAL(18,2)
    DECLARE @locUOO DECIMAL(18,2)
    DECLARE @avgCost DECIMAL(18,2)
    DECLARE @locTotvl DECIMAL(18,2)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @autob CHAR(1)
    DECLARE @passMark INT

    -- Get product and location details from invoice line
    SELECT @prodCode = BKAR_INVL_PCODE, @locCode = BKAR_INVL_LOC, 
           @pqty = BKAR_INVL_PQTY, @invGroup = BKAR_INV_GROUP, 
           @autob = BKAR_INVL_AUTOB, @passMark = 8
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Check if inventory group is 'RMA' and auto-backorder flag is 'W'
    IF @invGroup = 'RMA' AND @autob = 'W'
    BEGIN
        -- Find the warehouse inventory location record
        SELECT @locUOH = BKIC_LOCW_UOH, @locUOO = BKIC_LOCW_UOO, 
               @avgCost = BKIC_LOCW_AVGC
        FROM BKICLOCW
        WHERE BKIC_LOCW_PROD = @prodCode
          AND BKIC_LOCW_CODE = @locCode;

        -- Adjust warehouse inventory quantities
        SET @locUOH = @locUOH - @pqty;
        SET @locTotvl = @locUOH + @locUOO;  -- Calculate total value in warehouse location

        -- Recalculate average cost if necessary
        IF @locTotvl <> 0 AND (@locUOH + @locUOO) <> 0
        BEGIN
            SET @avgCost = @locTotvl / (@locUOH + @locUOO);
        END

        -- Markpoint 8 before saving changes
        EXEC markpoint_8_SaveToWarehouseInventory @invoiceNum, @lineNum, 0;

        -- Update warehouse location inventory
        UPDATE BKICLOCW
        SET BKIC_LOCW_UOH = @locUOH,
            BKIC_LOCW_AVGC = @avgCost
        WHERE BKIC_LOCW_PROD = @prodCode
          AND BKIC_LOCW_CODE = @locCode;

        -- Markpoint 8 after saving changes
        EXEC markpoint_8_SaveToWarehouseInventory @invoiceNum, @lineNum, 1;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Product and Location Lookup**:
   - The function retrieves the product code, location, and other details from the invoice line (`BKAR_INVL_PCODE`, `BKAR_INVL_LOC`, `BKAR_INVL_PQTY`, `BKAR_INV_GROUP`, `BKAR_INVL_AUTOB`).

2. **RMA and Auto-Backorder Check**:
   - **Condition**: The function checks if the inventory group is `RMA` (returns) and the auto-backorder flag (`BKAR_INVL_AUTOB`) is set to `W`.
   - If both conditions are met, the function proceeds to adjust the warehouse inventory location (`BKICLOCW`).

3. **Warehouse Inventory Location Lookup**:
   - The function retrieves the current warehouse inventory location quantities (`BKIC_LOCW_UOH`, `BKIC_LOCW_UOO`) and the average cost (`BKIC_LOCW_AVGC`).

4. **Inventory Adjustments**:
   - The function decreases the quantity on hand (`UOH`) in the warehouse by the product quantity from the invoice line (`BKAR_INVL_PQTY`).
   - The total value for the warehouse location is calculated as the sum of the quantity on hand and the quantity on order (`UOH + UOO`).
   - The average cost (`AVGC`) is recalculated if the total value and the sum of `UOH` and `UOO` are non-zero.

5. **Markpoint 8 Execution**:
   - The system executes `markpoint_8_SaveToWarehouseInventory` both before and after saving the changes to track the update progress.

6. **Warehouse Inventory Update**:
   - The function updates the warehouse inventory location (`BKICLOCW`) with the new quantity on hand and average cost after the adjustments are made.

### Error Handling:
- If the inventory group is not `RMA` or the auto-backorder flag is not set to `W`, the function skips any warehouse inventory adjustments and exits early.
- Errors such as invalid inserts or missing required fields should raise exceptions that log the error and stop further processing.

### Testing:

1. **Test RMA with Auto-Backorder**:
   - Create test cases where the invoice group is `RMA` and the auto-backorder flag is set to `W`. Ensure that the function correctly adjusts the warehouse inventory quantities and recalculates the average cost.
   - Ensure that `markpoint_8_SaveToWarehouseInventory` is called correctly both before and after the updates.

2. **Test Non-RMA Transactions**:
   - Create test cases where the invoice group is not `RMA` or the auto-backorder flag is not `W`. Ensure that the function exits early without making any updates to the warehouse inventory.

3. **Test Warehouse Inventory Adjustments**:
   - Create test cases with varying quantities and product types to ensure that the function correctly adjusts the quantity on hand (`UOH`) and recalculates the average cost based on the warehouse inventory data.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to Warehouse Inventory**: Ensure the `post_to_gl2` logic handles all the necessary inventory and warehouse updates. This function should update both the warehouse and general ledger if necessary.
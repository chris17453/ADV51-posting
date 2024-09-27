# Markpoint 7: Update Inventory Location

### Summary
This function updates the inventory location based on the product code and location from the invoice. If the product type is valid and not marked as "N" (non-inventory), the function adjusts inventory values such as quantity on hand (UOH) and quantity on sales order (UOSO) for returns (RMAs). It also updates the average cost (`BKIC_LOC_AVGC`) if necessary.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_7_UpdateInventoryLocation (
    @invoiceNum VARCHAR(20),
    @lineNum INT
)
AS
BEGIN
    DECLARE @prodCode VARCHAR(20)
    DECLARE @locCode VARCHAR(10)
    DECLARE @prodType CHAR(1)
    DECLARE @invGroup VARCHAR(3)
    DECLARE @autob CHAR(1)
    DECLARE @pqty DECIMAL(18,2)
    DECLARE @avgCost DECIMAL(18,2)
    DECLARE @locUOH DECIMAL(18,2)
    DECLARE @locUOSO DECIMAL(18,2)
    DECLARE @locITRNS DECIMAL(18,2)
    DECLARE @locTotvl DECIMAL(18,2)
    DECLARE @passMark INT
    DECLARE @postAmtTemp DECIMAL(18,2)

    -- Get product and location details from invoice line
    SELECT @prodCode = BKAR_INVL_PCODE, @locCode = BKAR_INVL_LOC, 
           @invGroup = BKAR_INV_GROUP, @autob = BKAR_INVL_AUTOB, 
           @pqty = BKAR_INVL_PQTY, @passMark = 7
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Find the product master record based on product code
    SELECT @prodType = BKIC_PROD_TYPE
    FROM BKICMSTR
    WHERE BKIC_PROD_CODE = @prodCode;

    -- Check if product type is valid and not "N" (non-inventory)
    IF @prodType IS NULL OR @prodType = 'N'
    BEGIN
        RETURN 0; -- Exit if product is non-inventory or invalid
    END

    -- Find inventory location record based on product code and location
    SELECT @avgCost = BKIC_LOC_AVGC, @locUOH = BKIC_LOC_UOH, 
           @locUOSO = BKIC_LOC_UOSO, @locITRNS = BKIC_LOC_ITRNS
    FROM BKICLOC
    WHERE BKIC_PROD_CODE = @prodCode
      AND BKIC_LOC = @locCode;

    -- Adjust values based on inventory group and auto-backorder flag
    IF @invGroup = 'RM'
    BEGIN
        -- For returns (RMA), adjust cost of goods sold and update inventory
        IF @passMark < 12
        BEGIN
            UPDATE BKARINVL
            SET BKAR_INVL_PCOGS = @avgCost
            WHERE BKAR_INV_NUM = @invoiceNum
              AND BKAR_INV_LINE = @lineNum;
        END

        -- Adjust inventory quantities
        IF @passMark < 7
        BEGIN
            IF @autob = 'W'
            BEGIN
                SET @locUOH = @locUOH + @pqty;  -- Increase quantity on hand for warehouse returns
            END

            SET @locUOSO = @locUOSO - @pqty;  -- Decrease quantity on sales order

            -- If not warehouse returns, update average cost
            IF @autob <> 'W'
            BEGIN
                SET @postAmtTemp = -1;  -- Set adjustment amount
                SET @locTotvl = @avgCost + @postAmtTemp;
                SET @avgCost = @locTotvl / (@locUOH + @locUOSO + @locITRNS);  -- Recalculate average cost
            END

            -- Markpoint 7 before updating inventory location
            EXEC markpoint_7_SaveToInventory @invoiceNum, @lineNum, 0;

            -- Update inventory location
            UPDATE BKICLOC
            SET BKIC_LOC_UOH = @locUOH,
                BKIC_LOC_UOSO = @locUOSO,
                BKIC_LOC_AVGC = @avgCost
            WHERE BKIC_PROD_CODE = @prodCode
              AND BKIC_LOC = @locCode;

            -- Markpoint 7 after updating inventory location
            EXEC markpoint_7_SaveToInventory @invoiceNum, @lineNum, 1;
        END
    END

    -- Update post status
    EXEC post_status;

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Product Code and Location Lookup**:
   - The function retrieves the product code and location from the invoice line (`BKAR_INVL_PCODE`, `BKAR_INVL_LOC`).
   - It checks the product type from the product master (`BKICMSTR`) table to ensure the product is inventory-based (not `N`).

2. **Inventory Location Lookup**:
   - The function retrieves the current inventory location details (`BKICLOC`) such as average cost (`BKIC_LOC_AVGC`), quantity on hand (`BKIC_LOC_UOH`), quantity on sales order (`BKIC_LOC_UOSO`), and inventory transactions (`BKIC_LOC_ITRNS`).

3. **Return Handling (RMA)**:
   - **Condition**: If the inventory group (`BKAR_INV_GROUP`) is `RM` (returns), and the `pass_mark` is less than `12`, the cost of goods sold (`BKAR_INVL_PCOGS`) is updated based on the average cost from `BKICLOC`.
   - If the `pass_mark` is less than `7`, the inventory quantities and average cost are adjusted.
     - **Warehouse Returns** (`autob = 'W'`): The quantity on hand (`UOH`) is increased by the product quantity from the invoice line.
     - **Non-Warehouse Returns** (`autob <> 'W'`): The average cost is recalculated based on the total value and updated quantities.

4. **Inventory Adjustments**:
   - The function updates the inventory location quantities (`UOH`, `UOSO`) and the average cost (`AVGC`) based on the adjustments made during the return processing.

5. **Markpoint 7 Execution**:
   - The system executes `markpoint_7_SaveToInventory` both before and after updating the inventory location to indicate when the updates occur.

6. **Post Status**:
   - After completing the inventory updates, the function calls `post_status` to ensure the status is updated correctly.

### Error Handling:
- If the product is non-inventory (`BKIC_PROD_TYPE = 'N'`) or if the product code is invalid, the function exits early without making any updates.
- Errors such as invalid inserts or missing required fields should raise exceptions that log the error and stop further processing.

### Testing:

1. **Test Return Handling**:
   - Create test cases where the product is part of an RMA (`invGroup = 'RM'`) to ensure that the function correctly updates the inventory quantities (`UOH`, `UOSO`) and recalculates the average cost (`AVGC`).
   - Ensure that `markpoint_7_SaveToInventory` is called correctly both before and after the updates.

2. **Test Non-Inventory Products**:
   - Create test cases where the product type is `N` (non-inventory) to ensure that the function exits early and does not make any updates.

3. **Test Warehouse vs Non-Warehouse Returns**:
   - Create test cases where the `autob` flag is either `W` (warehouse) or not `W` to ensure that the function handles these cases correctly by either adjusting the quantity on hand or recalculating the average cost.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to Inventory (`post_to_gl2`)**: This procedure handles the actual posting of inventory changes. Ensure that the procedure is correctly implemented and accepts the necessary parameters for updating inventory and recalculating costs.
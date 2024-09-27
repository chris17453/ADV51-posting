# Markpoint 26: Delete or Update Invoice Header

### Summary
This function either deletes the sales order (SO) from the `BKARINV` table if the invoice flag (`BKAR_INV_INVCD`) is set to `'Y'`, or it updates the invoice header to reset financial fields like subtotal, tax, and total to zero.

### SQL Function

```sql
CREATE PROCEDURE markpoint_26_DeleteOrUpdateInvoiceHeader (
    @invoiceNum VARCHAR(20),
)
AS
BEGIN
    DECLARE @invcd CHAR(1)
    DECLARE @soNumber VARCHAR(20)
    DECLARE @errMsg VARCHAR(255)

    -- Get the invoice header details
    SELECT @invcd = BKAR_INV_INVCD, @soNumber = BKAR_INV_SONUM
    FROM BKARINV
    WHERE BKAR_INV_NUM = @invoiceNum;

    IF @invcd = 'Y'
    BEGIN
        -- If the invoice is confirmed ('Y'), delete the sales order
        EXEC markpoint 26, @invoiceNum, 0;

        DELETE FROM BKARINV
        WHERE BKAR_INV_NUM = @invoiceNum;

        -- Markpoint 26 after deletion
        EXEC markpoint 26, @invoiceNum, 1;

        -- Check for errors in deletion
        IF @@ROWCOUNT = 0
        BEGIN
            SET @errMsg = 'Unable to delete SO #' + @soNumber + '. Please delete it manually under SO-A.';
            RAISERROR(@errMsg, 16, 1);
        END
    END
    ELSE
    BEGIN
        -- Reset invoice financial fields if not confirmed
        UPDATE BKARINV
        SET BKAR_INV_LINV_P = @invoiceNum,
            BKAR_INV_SUBTOT = 0,
            BKAR_INV_TAXAMT = 0,
            BKAR_INV_TOTAL = 0,
            BKAR_INV_FRGHT = 0,
            BKAR_INV_FUEL = 0
        WHERE BKAR_INV_NUM = @invoiceNum;

        -- Markpoint 26 after update
        EXEC markpoint 26, @invoiceNum, 1;
    END


    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Header Lookup**:
   - The function retrieves the `BKAR_INV_INVCD` flag and the sales order number (`BKAR_INV_SONUM`) for the provided invoice number from the `BKARINV` table.

2. **Condition for Deletion**:
   - **Condition**: If `BKAR_INV_INVCD = 'Y'`, the function deletes the sales order from the `BKARINV` table.

3. **Markpoint 26 Execution for Deletion**:
   - The system executes `markpoint_26_SaveToHeader` both before and after deleting the sales order to track the update progress.
   - The function checks if the deletion was successful by verifying `@@ROWCOUNT`. If the deletion fails, an error message is raised.

4. **Condition for Update**:
   - **Condition**: If `BKAR_INV_INVCD` is not `'Y'`, the function resets financial fields like `BKAR_INV_SUBTOT`, `BKAR_INV_TAXAMT`, `BKAR_INV_TOTAL`, `BKAR_INV_FRGHT`, and `BKAR_INV_FUEL` to zero.

5. **Markpoint 26 Execution for Update**:
   - The system executes `markpoint_26_SaveToHeader` after resetting the fields to track the update progress.

6. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If the sales order cannot be deleted, the function raises an error indicating manual deletion is required.

### Testing:

1. **Test Sales Order Deletion**:
   - Create test cases where `BKAR_INV_INVCD = 'Y'`. Ensure that the function correctly deletes the sales order from `BKARINV`.

2. **Test Invoice Header Reset**:
   - Create test cases where `BKAR_INV_INVCD != 'Y'`. Ensure that the function correctly resets the invoice financial fields (`BKAR_INV_SUBTOT`, `BKAR_INV_TAXAMT`, etc.) to zero.

3. **Test Failed Deletion**:
   - Create test cases where the sales order deletion fails. Ensure that the function raises an appropriate error message.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly handles locking.

### Notes:
- **Deletion vs. Reset**: Ensure that the logic for deletion (when `BKAR_INV_INVCD = 'Y'`) and the reset of financial fields (when `BKAR_INV_INVCD != 'Y'`) is handled correctly.
- **Markpoint Logging**: The use of `markpoint_26_SaveToHeader` ensures that the deletion or update process is tracked, which can be useful for debugging or auditing purposes.
# Markpoint 17: Delete Invoice Line Item

### Summary
This function deletes an invoice line item from the `BKARINVL` table. The `mark_point` is used to track the deletion process both before and after the deletion of the line item.
- This is a PER INVOICE LINE item iteration.


### SQL Function

```sql
CREATE PROCEDURE markpoint_17_DeleteInvoiceLineItem (
    @invoiceNum VARCHAR(20),
    @lineNum INT,
    @post_nolock BIT = 0
)
AS
BEGIN
    DECLARE @currLine INT = @lineNum

    -- Markpoint 17 before deletion
    EXEC markpoint_17_SaveBeforeDelete @invoiceNum, @currLine, 0;

    -- Delete the invoice line item from BKARINVL
    DELETE FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Markpoint 17 after deletion
    EXEC markpoint_17_SaveBeforeDelete @invoiceNum, @currLine, 1;

    -- Post lock check
    IF @post_nolock = 0
    BEGIN
        RETURN quit_posting(16, @lineNum);
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Line Item Deletion**:
   - The function deletes the invoice line item from the `BKARINVL` table where the invoice number and line number match the provided parameters.

2. **Markpoint 17 Execution**:
   - The system executes `markpoint_17_SaveBeforeDelete` both before and after the deletion to track the process. This ensures that the deletion is correctly marked in the system logs.


### Error Handling:
- If the line item is not found, the deletion should raise an error or simply skip the deletion, depending on the system's handling of missing records.
- Lock handling is performed by checking `post_nolock` to ensure that the system handles locked records properly.

### Testing:

1. **Test Line Item Deletion**:
   - Create test cases where an invoice line item is deleted from `BKARINVL`. Ensure that the function correctly removes the record.

2. **Test Skip Deletion**:
   - Create test cases where no matching line item exists in `BKARINVL`. Ensure that the function does not raise errors unnecessarily and gracefully handles the case where no line item is found.

3. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly handles locking.

### Notes:
- **Line Item Deletion**: Ensure that the `BKARINVL` table is properly set up to handle line item deletions without causing referential integrity issues.
- **Markpoint Logging**: The use of `markpoint_17_SaveBeforeDelete` ensures that the deletion process is tracked, which can be useful for debugging or auditing purposes.
# Markpoint 23: Delete Invoice Sales Lines

## Summary:
This function deletes all sales lines associated with an invoice by using `mark_point 23`. The function sets the mark point, deletes the associated sales lines in one step, and then completes the mark point.

## MSSQL Function

```sql
CREATE PROCEDURE Markpoint23_DeleteInvoiceSalesLines
    @invoice_number VARCHAR(15)
AS
BEGIN
    -- Set the mark point to 23 (beginning of the operation)
    EXEC mark_point 23, 0, False;

    -- Delete all sales lines associated with the invoice
    DELETE FROM BKARINVL
    WHERE BKAR_INVL_INVNM = @invoice_number;

    -- Complete the mark point for 23
    EXEC mark_point 23, 0, True;

END
GO
```

### Breakdown of Tasks:

1. **Set Markpoint 23 (Start):**
   - The `mark_point` function is used to indicate the beginning of the deletion process for mark point 23.

2. **Delete Sales Lines:**
   - A single `DELETE` statement removes all sales lines from the `BKARINVL` table that are associated with the provided invoice number (`BKAR_INVL_INVNM`).

3. **Complete Markpoint 23 (End):**
   - The `mark_point` function is used again to indicate the completion of mark point 23 after the delete operation.

### Error Handling:

- If the `DELETE` operation fails (due to missing records, database constraints, etc.), make sure to include proper error handling using `TRY...CATCH` to capture and log the error appropriately.

### Testing:

- **Test Case 1: Standard Invoice**
  - Run the function with a standard invoice and verify that all associated sales lines are deleted correctly and mark point 23 is set and completed.

- **Test Case 2: No Sales Lines**
  - Run the function with an invoice that has no associated sales lines and ensure that the function completes without errors.

- **Test Case 3: Error Handling**
  - Introduce invalid data (e.g., an invalid invoice number) and confirm that errors are handled properly without crashing the system.

### Notes:

- **Performance Considerations:** The `DELETE` operation should be efficient even with large numbers of records since it’s executed as a single operation.
- **Record Locking:** Ensure that the appropriate locks are applied to avoid any concurrency issues when deleting sales lines associated with an invoice.
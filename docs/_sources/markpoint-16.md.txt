
# Markpoint 16: Archive Invoice Line Items

### Summary
This function handles archiving line items from the invoice into the historical table (`BKARHIVL`) if the item type is `'X'` or the product code is empty. It marks the point before and after saving the line item into the historical table.
- This is a PER INVOICE LINE item iteration.

### SQL Function

```sql
CREATE PROCEDURE markpoint_16_ArchiveInvoiceLineItem (
    @invoiceNum VARCHAR(20),
    @lineNum INT,
)
AS
BEGIN
    DECLARE @itemType CHAR(1)
    DECLARE @prodCode VARCHAR(20)
    DECLARE @currLine INT
    DECLARE @archiveNum VARCHAR(20)

    -- Get the line item details
    SELECT @itemType = UPPER(BKAR_INVL_ITYPE), @prodCode = BKAR_INVL_PCODE, 
           @currLine = BKAR_INVL_LINE, @archiveNum = BKAR_INV_NUM
    FROM BKARINVL
    WHERE BKAR_INV_NUM = @invoiceNum
      AND BKAR_INV_LINE = @lineNum;

    -- Check if the item type is 'X' or product code is empty
    IF @itemType = 'X' OR @prodCode = ''
    BEGIN
        -- Markpoint 16 before saving
        EXEC markpoint 16, @invoiceNum, @lineNum, 0;

        -- Archive the invoice line item to the historical table
        INSERT INTO BKARHIVL (
            BKAR_HIVL_INVNM, BKAR_HIVL_LINE, BKAR_HIVL_ITYPE, BKAR_HIVL_PCODE, 
            BKAR_HIVL_QTY, BKAR_HIVL_PRICE, BKAR_HIVL_TOTAL, BKAR_HIVL_DATE
        )
        SELECT BKAR_INV_NUM, BKAR_INVL_LINE, BKAR_INVL_ITYPE, BKAR_INVL_PCODE, 
               BKAR_INVL_PQTY, BKAR_INVL_PRICE, BKAR_INVL_TOTAL, BKAR_INV_INVDTE
        FROM BKARINVL
        WHERE BKAR_INV_NUM = @invoiceNum
          AND BKAR_INV_LINE = @lineNum;

        -- Markpoint 16 after saving
        EXEC markpoint 16, @invoiceNum, @lineNum, 1;
    END

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Invoice Line Item Lookup**:
   - The function retrieves the item type (`BKAR_INVL_ITYPE`), product code (`BKAR_INVL_PCODE`), and current line number from the invoice line.

2. **Condition for Archiving**:
   - **Condition**: The function proceeds if the item type is `'X'` or the product code is empty.

3. **Markpoint 16 Execution**:
   - The system executes `markpoint_16_SaveToArchive` both before and after saving to track the update progress.

4. **Archive Line Item**:
   - The function inserts the invoice line item into the historical table (`BKARHIVL`), copying the relevant details like invoice number, line number, item type, product code, quantity, price, total, and invoice date.

5. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If the line item is not eligible for archiving (item type is not `'X'` and product code is not empty), the function skips the archival process.
- If any required fields are missing or invalid, the function should raise an error and prevent the transaction from being saved.

### Testing:

1. **Test Archiving for Item Type 'X'**:
   - Create test cases where the line item has an item type of `'X'`. Ensure that the function correctly archives the line item into `BKARHIVL`.

2. **Test Archiving for Empty Product Code**:
   - Create test cases where the product code is empty (`BKAR_INVL_PCODE = ''`). Ensure that the function correctly archives the line item into `BKARHIVL`.

3. **Test Skip Archiving**:
   - Create test cases where the item type is not `'X'` and the product code is not empty. Ensure that the function does not archive the line item.

### Notes:
- **Historical Table Insertion**: Ensure that the historical table (`BKARHIVL`) is properly set up to receive the archived line item details.
- **Post Lock Handling**: If the `post_nolock` flag is set, the function skips saving the transaction.
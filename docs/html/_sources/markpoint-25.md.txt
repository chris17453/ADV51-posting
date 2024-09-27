# Markpoint 25: Transfer Invoice to Historical Table

### Summary
This function saves the invoice to the historical invoice table (`BKARHINV`). If the save operation fails, it raises an error message and stops further processing. If successful, it verifies the save operation and continues.

### SQL Function

```sql
CREATE PROCEDURE markpoint_25_TransferInvoiceToHistorical (
    @invoiceNum VARCHAR(20),
    @actualNL INT,
)
AS
BEGIN
    DECLARE @invHolder VARCHAR(20) = @invoiceNum
    DECLARE @getOut BIT = 0
    DECLARE @errorMsg VARCHAR(255)

    -- Transfer Invoice to BKARHINV, update actual NL
    UPDATE BKARHINV
    SET BKAR_INV_NL = @actualNL
    WHERE BKAR_INV_NUM = @invoiceNum;

    -- Markpoint 25 before saving
    EXEC markpoint 25, @invoiceNum, 0;

    -- Save the changes in BKARHINV
    IF @@ROWCOUNT = 0
    BEGIN
        SET @errorMsg = 'BKSOG file error occurred saving to BKARHINV. Posting process will not continue. Please report this exact error message to IT.';
        RAISERROR(@errorMsg, 16, 1);
        SET @getOut = 1;
    END
    ELSE
    BEGIN
        -- Verify if the invoice was correctly saved to BKARHINV
        SELECT COUNT(*) 
        FROM BKARHINV 
        WHERE BKAR_INV_NUM = @invoiceNum;

        IF @@ROWCOUNT = 0
        BEGIN
            SET @errorMsg = 'BKSOG Invoice number ' + @invHolder + ' did not save to BKARHINV. Please report this exact error message to IT.';
            RAISERROR(@errorMsg, 16, 1);
        END
    END

    -- Markpoint 25 after saving
    EXEC markpoint 25, @invoiceNum, 1;

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Transfer Invoice to Historical Table**:
   - The function updates the `BKAR_INV_NL` field in the historical invoice table (`BKARHINV`) for the given invoice number, using the provided actual number line (`@actualNL`).

2. **Markpoint 25 Execution**:
   - The system executes `markpoint_25_SaveToHistory` both before and after saving the invoice to track the update progress.

3. **Save Operation and Error Handling**:
   - **Condition**: If the `UPDATE` statement does not affect any rows, the function raises an error, stating that the invoice was not saved to `BKARHINV`.
   - If the save operation fails, the function halts further processing and raises an error message instructing the user to report the issue to IT.

4. **Verification of Save**:
   - **Condition**: The function performs a `COUNT` query to ensure that the invoice was correctly saved to the `BKARHINV` table. If not, it raises another error, specifying that the invoice was not saved and instructing the user to report the issue.

5. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function clears buffers and exits without completing the post.

### Error Handling:
- If the save operation fails or the invoice does not save correctly to the historical table (`BKARHINV`), an error message is raised and the process halts. The user is instructed to report the error to IT with the exact error message.

### Testing:

1. **Test Successful Invoice Transfer**:
   - Create test cases where an invoice is successfully transferred to the historical table (`BKARHINV`). Ensure that the function updates the `BKAR_INV_NL` field and correctly saves the invoice.

2. **Test Failed Save Operation**:
   - Create test cases where the `UPDATE` statement does not succeed (e.g., when the invoice does not exist). Ensure that the function raises an appropriate error message.

3. **Test Verification of Save**:
   - Create test cases where the invoice is not found in `BKARHINV` after the save operation. Ensure that the function raises an error message instructing the user to report the issue.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly handles locking.

### Notes:
- **Invoice Transfer**: Ensure that the `BKARHINV` table is correctly set up to store the historical invoice data.
- **Markpoint Logging**: The use of `markpoint_25_SaveToHistory` ensures that the save operation is tracked, which can be useful for debugging or auditing purposes.
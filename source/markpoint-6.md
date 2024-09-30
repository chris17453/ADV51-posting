# Markpoint 6: Post Fuel Charges

### Summary
This function posts fuel charges to the general ledger if the fuel amount is not zero. The general ledger account is selected based on the customer class. If the customer class is `GP`, a specific GL account is used; otherwise, a different GL account is assigned. The department code for fuel is based on the invoice location.

### SQL Function

```sql
CREATE PROCEDURE markpoint_6_PostFuelToGL (
    @invoiceNum VARCHAR(20)
)
AS
BEGIN
    DECLARE @fuel_glacct VARCHAR(10)
    DECLARE @invFuel DECIMAL(18,2)
    DECLARE @invLoc VARCHAR(3)
    DECLARE @cusClass VARCHAR(10)
    DECLARE @post_nolock BIT = 0

    -- Get invoice details
    SELECT @invFuel = BKAR_INV_FUEL, @invLoc = LEFT(BKAR_INV_LOC, 3)
    FROM BKARINV
    WHERE BKAR_INV_NUM = @invoiceNum;

    -- If fuel is zero, exit function
    IF @invFuel = 0
    BEGIN
        RETURN 0;
    END

    -- Get customer class
    SELECT @cusClass = BKAR_CLASS
    FROM BKARCUST
    WHERE BKAR_CUSTCODE = (SELECT BKAR_INV_CUSCOD FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum);

    -- Determine GL account for fuel based on customer class
    IF @cusClass = 'GP'
    BEGIN
        SET @fuel_glacct = '40515     '
    END
    ELSE
    BEGIN
        SET @fuel_glacct = '40510     '
    END

    -- Markpoint 6 before posting
    EXEC markpoint_6_SaveToGL @invoiceNum, 0;

    -- Post to general ledger using `post_to_gl2` function
    EXEC post_to_gl2 @fuel_glacct, @invLoc, 'Fuel from Invoice', @invFuel, 
                     @invoiceNum, GETDATE(), 'FUEL', NULL, 0, 'Y';

    -- Post lock check
    IF @post_nolock = 0
    BEGIN
        RETURN quit_posting(4,0);
    END

    -- Markpoint 6 after successful posting
    EXEC markpoint_6_SaveToGL @invoiceNum, 1;

    RETURN 0;
END
GO
```

### Breakdown of Actions:

1. **Fuel Amount Check**:
   - **Condition**: The function checks if the fuel amount (`BKAR_INV_FUEL`) is non-zero. If the fuel amount is `0`, the function exits without making any changes.

2. **Customer Class Lookup**:
   - **Condition**: The function retrieves the customer class (`BKAR_CLASS`) based on the customer code from the invoice.
   - **Action**: The fuel GL account (`fuel_glacct`) is determined based on the customer class:
     - If the customer class is `GP`, the GL account is set to `'40515'`.
     - Otherwise, the GL account is set to `'40510'`.

3. **Department Code Assignment**:
   - The fuel department code (`BKSY_AR_FRGTDPT`) is set to the first three characters of the invoice location (`BKAR_INV_LOC`).

4. **General Ledger Posting**:
   - The function uses the `post_to_gl2` function to post the fuel charges to the general ledger. The function passes the fuel GL account, department, description, fuel amount, invoice number, and other required details to `post_to_gl2`.

5. **Lock Handling**:
   - If the `post_nolock` flag is not set (`post_nolock = 0`), the function calls `quit_posting` to terminate further processing.

6. **Markpoint 6 Execution**:
   - The system executes `markpoint_6_SaveToGL` both before and after the posting action to indicate when the general ledger updates occur.

### Error Handling:
- If no valid customer class is found or the fuel amount is `0`, the function returns early without posting any fuel charges.
- Errors such as invalid inserts or missing required fields should raise exceptions that log the error and stop further processing.

### Testing:

1. **Test Fuel Posting**:
   - Create test cases where the fuel amount is non-zero to ensure the function correctly posts the fuel charges to the general ledger based on the customer class.
   - Ensure that `markpoint_6_SaveToGL` is called correctly both before and after the posting.

2. **Test Fuel Amount Zero**:
   - Create test cases where the fuel amount is `0` to ensure the function exits without making any changes.

3. **Test Customer Class 'GP'**:
   - Create test cases where the customer class is `GP` to ensure the correct GL account (`40515`) is used for posting fuel charges.

4. **Test Post Lock Handling**:
   - Test scenarios where the `post_nolock` flag is either set or not set to ensure the function correctly calls `quit_posting` when required.

### Notes:
- **Post to General Ledger (`post_to_gl2`)**: This procedure handles the actual posting of fuel charges to the general ledger. Ensure that the procedure is correctly implemented and accepts the following parameters:
  - Account
  - Department
  - Description (Fuel from Invoice)
  - Total Amount (Fuel)
  - Invoice Number
  - Invoice Date
  - Posting Type (`FUEL`)
  - Customer Code (optional)
  - Lock Flag (`False`)
  - Confirmation (`Y`)

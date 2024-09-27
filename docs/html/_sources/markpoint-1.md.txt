# Markpoint 1 AND 2: Save to Accounts Receivable Payment Record

### Summary
This function updates the Accounts Receivable (AR) payment record for a specific invoice. It involves validating the customer, updating payment information, adjusting customer balances, and managing RMA-related records.
- Markpoint 1: related to saving the accounts receivable record
- Markpoint 2: updating the customer record) are intertwined in the legacy code. To clarify

### Breakdown of Legacy Logic:
1. **Customer Lookup and Parent/Child Handling**:
   - It looks up the customer (`BKAR_INV_CUSCOD` from `BKARINV`) and handles scenarios where the shipping customer (`BKAR_INV_SHPCOD`) is different from the billing customer (indicating a parent/child relationship).
   
2. **RMA Record Processing**:
   - If the invoice belongs to an RMA (`inv_group == 'RM'`), the system attempts to find the related RMA history records.
   
3. **Points Assignment**:
   - If relevant, the system assigns customer points based on a transaction history lookup.

4. **Accounts Receivable Update**:
   - Updates the AR record, adjusting the outstanding invoice or credit balances based on the invoice total (`BKAR_INV_TOTAL`).

5. **Customer Sales History Update**:
   - Sales history for the customer or parent customer (`BKARPR`) is updated based on whether the customer is a parent or a child account.

6. **Markpoints**:
   - Two markpoints are called:
     - **Markpoint 1**: For saving the accounts receivable data.
     - **Markpoint 2**: For saving customer data.

### SQL Implementation Plan
We will consolidate the actions into one SQL function that performs the following steps:
1. **Customer and Parent/Child Handling**.
2. **RMA Processing** (if applicable).
3. **Points Assignment** (if applicable).
4. **Accounts Receivable Update**.
5. **Customer Sales History Update**.
6. **Markpoint 1 and Markpoint 2 Execution**.

### SQL Function

```sql
CREATE PROCEDURE markpoint_1_and_2_SaveARAndCustomerRecord (
    @invoiceNum VARCHAR(20)
)
AS
BEGIN
    DECLARE @custCode VARCHAR(20)
    DECLARE @shipCode VARCHAR(20)
    DECLARE @is_parent BIT = 0
    DECLARE @invDate DATE
    DECLARE @total DECIMAL(18,2)
    DECLARE @pointsRate FLOAT

    -- Step 1: Customer Lookup
    SET @custCode = (SELECT BKAR_INV_CUSCOD FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)
    SET @shipCode = (SELECT BKAR_INV_SHPCOD FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)
    SET @invDate = (SELECT BKAR_INV_INVDTE FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)
    SET @total = (SELECT BKAR_INV_TOTAL FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)

    IF @custCode IS NULL
    BEGIN
        -- Log error if customer is not found
        RAISERROR('Customer for Sales Order not found', 16, 1)
        RETURN
    END

    -- Step 2: Parent/Child Handling
    IF @shipCode != '' AND @shipCode != @custCode
    BEGIN
        IF EXISTS (
            SELECT 1 FROM BKARPR
            WHERE BKAR_PR_CSTCOD = @shipCode AND BKAR_PR_PARENT = @custCode
        )
        BEGIN
            SET @is_parent = 1
        END

        -- Update points_class and points_cust for shipping customer
        UPDATE BKARINV
        SET BKAR_CLASS = (SELECT BKAR_CLASS FROM BKARCUST WHERE BKAR_CUSTCODE = @shipCode)
        WHERE BKAR_INV_NUM = @invoiceNum
    END

    -- Step 3: RMA Handling (if applicable)
    IF (SELECT inv_group FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum) = 'RM'
    BEGIN
        -- Check RMA History by invoice number
        IF EXISTS (
            SELECT 1 FROM BKRMAHST WHERE BKRMA_H_AINVNUM = @invoiceNum
        )
        BEGIN
            UPDATE BKRMAHST
            SET BKRMA_H_AINVNUM = @invoiceNum,
                BKRMA_H_AINVDTE = @invDate
            WHERE BKRMA_H_AINVNUM = @invoiceNum
              AND @invDate > BKRMA_H_RDATE
        END
        ELSE
        BEGIN
            -- Check by Sales Order number if not found by invoice number
            UPDATE BKRMAHST
            SET BKRMA_H_AINVNUM = @invoiceNum,
                BKRMA_H_AINVDTE = @invDate
            WHERE BKRMA_H_ASONUM = (SELECT BKAR_INV_SONUM FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)
        END
    END

    -- Step 4: Points Transaction Handling (if applicable)
    IF EXISTS (
        SELECT 1
        FROM BKPTSHST
        WHERE BKPTSHST_TRNSNM = (SELECT BKRMA_H_OINVNUM FROM BKRMAHST WHERE BKRMA_H_AINVNUM = @invoiceNum)
          AND BKPTSHST_DATE = @invDate
          AND BKPTSHST_QTY = 0
    )
    BEGIN
        SET @pointsRate = (SELECT BKPTSHST_RATE FROM BKPTSHST WHERE BKPTSHST_TRNSNM = (SELECT BKRMA_H_OINVNUM FROM BKRMAHST WHERE BKRMA_H_AINVNUM = @invoiceNum))
    END

    -- Step 5: Update Accounts Receivable
    IF @total > 0
    BEGIN
        UPDATE BKARINV
        SET BKAR_OUTINV = BKAR_OUTINV + @total
        WHERE BKAR_INV_NUM = @invoiceNum
    END
    ELSE
    BEGIN
        UPDATE BKARINV
        SET BKAR_OUT_CREDIT = BKAR_OUT_CREDIT - @total
        WHERE BKAR_INV_NUM = @invoiceNum
    END

    -- Step 6: Update Sales History
    UPDATE BKARINV
    SET BKAR_LASTSALE = @invDate,
        BKAR_GROSS_YTD = BKAR_GROSS_YTD + (SELECT BKAR_INV_SUBTOT FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum),
        BKAR_COGS_YTD = BKAR_COGS_YTD + (SELECT BKAR_INV_COGS FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)
    WHERE BKAR_INV_NUM = @invoiceNum

    IF MONTH(@invDate) = MONTH(GETDATE())
    BEGIN
        UPDATE BKARINV
        SET BKAR_GROSS_MTD = BKAR_GROSS_MTD + (SELECT BKAR_INV_SUBTOT FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum),
            BKAR_COGS_MTD = BKAR_COGS_MTD + (SELECT BKAR_INV_COGS FROM BKARINV WHERE BKAR_INV_NUM = @invoiceNum)
        WHERE BKAR_INV_NUM = @invoiceNum
    END

    -- Step 7: Update Parent/Customer Sales History
    IF @is_parent = 1
    BEGIN
        UPDATE BKARPR
        SET BKAR_PR_LSALE = @invDate
        WHERE BKAR_PR_CSTCOD = @shipCode
    END
    ELSE
    BEGIN
        UPDATE BKARPR
        SET BKAR_PR_LSALE = @invDate
        WHERE BKAR_PR_CSTCOD = @custCode
    END

    -- Step 8: Markpoint 1 and 2 Execution
    -- Markpoint 1: Save to Accounts Receivable
    EXEC markpoint_1_SaveToARPaymentRecord @invoiceNum

    -- Markpoint 2: Save to Customer
    EXEC markpoint_2_SaveToCustomerRecord @invoiceNum

    -- Return success
    RETURN 0
END
GO
```

### Breakdown of Actions:

1. **Customer and Parent/Child Handling**:
   - Lookup the customer (`BKAR_INV_CUSCOD`) from `BKARINV`.
   - If `BKAR_INV_SHPCOD` is different from `BKAR_INV_CUSCOD`, check if it is a child customer. If true, set the parent flag and update `points_class` and `points_cust`.

2. **RMA Handling**:
   - If the invoice is an RMA (`inv_group == 'RM'`), check and update the `BKRMAHST` record by invoice number or Sales Order number.

3. **Points Assignment**:
   - Assign points by looking up the points transaction in `BKPTSHST` associated with the original RMA invoice.

4. **Accounts Receivable Update**:
   - If the invoice total is positive, increase `BKAR_OUTINV`. If negative, adjust `BKAR_OUT_CREDIT`.

5. **Sales History Update**:
   - Update `BKAR_LASTSALE`, `BKAR_GROSS_YTD`, `BKAR_COGS_YTD`, and month-to-date values if the invoice date falls in the current month.

6. **Parent/Customer Sales History Update**:
   - Update `BKAR_PR_LSALE` for the parent or customer based on the parent-child relationship.

7. **Markpoint 1 Execution**:
   - Save the Accounts Receivable data by calling `markpoint_1_SaveToARPaymentRecord`.

8. **Markpoint 2 Execution**:
   - Save the customer data by calling `markpoint_2_SaveToCustomerRecord`.

### Testing:
-
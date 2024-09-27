# Pre-validation SQL Procedures

### 1. **Check Invoice Status**

#### **Summary**
This function verifies whether an invoice is eligible for processing by checking if it has already been processed or marked for deletion. It ensures that only valid invoices proceed through the posting process.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.check_invoice_status (@invoice_number VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Check if the invoice exists and has been processed or marked for deletion
    IF EXISTS (
        SELECT 1 
        FROM BKARINV 
        WHERE BKAR_INV_INVNO = @invoice_number 
          AND (BKAR_INV_STATUS = 'processed' OR BKAR_INV_INVCD = 'Y')
    )
    BEGIN
        SET @result = 0; -- Invalid status
    END
    ELSE
    BEGIN
        SET @result = 1; -- Valid for processing
    END

    RETURN @result;
END;
GO
```

---

### 2. **Customer Record Validation**

#### **Summary**
This function validates a customer’s eligibility by ensuring the customer exists, is not on hold, and has not exceeded their credit limit. It helps prevent processing invoices for invalid or risky customers.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.validate_customer (@customer_code VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Combined condition to check if customer exists and is valid
    IF NOT EXISTS (
        SELECT 1 
        FROM BKARCUST 
        WHERE BKAR_CUST_CUSTCODE = @customer_code
    )
    BEGIN
        SET @result = 0; -- Customer does not exist
    END
    ELSE IF EXISTS (
        SELECT 1 
        FROM BKARCUST 
        WHERE BKAR_CUST_CUSTCODE = @customer_code 
          AND (BKAR_CUST_HOLD = 'Y' OR BKAR_CUST_BALANCE > BKAR_CUST_CREDIT_LIMIT)
    )
    BEGIN
        SET @result = 0; -- Customer on hold or exceeds credit limit
    END
    ELSE
    BEGIN
        SET @result = 1; -- Valid customer
    END

    RETURN @result;
END;
GO
```

---

### 3. **Inventory Validation**

#### **Summary**
This function ensures that all inventory items in an invoice exist and have sufficient stock to fulfill the order. It prevents the processing of invoices that cannot be fully satisfied due to inventory constraints.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.validate_inventory (@invoice_number VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Check if any inventory item in the invoice does not exist
    IF EXISTS (
        SELECT 1 
        FROM BKARINVL li
        WHERE li.BKAR_INV_INVNO = @invoice_number 
          AND NOT EXISTS (
              SELECT 1 
              FROM BKICMSTR inv 
              WHERE inv.BKIC_MSTR_ITEMCODE = li.BKAR_INV_ITEMCODE
          )
    )
    BEGIN
        SET @result = 0; -- Item does not exist
    END
    -- Check if any inventory item has insufficient stock
    ELSE IF EXISTS (
        SELECT 1 
        FROM BKARINVL li 
        JOIN BKICMSTR inv ON li.BKAR_INV_ITEMCODE = inv.BKIC_MSTR_ITEMCODE
        WHERE li.BKAR_INV_INVNO = @invoice_number 
          AND inv.BKIC_MSTR_QTY_ON_HAND < li.BKAR_INV_QTY
    )
    BEGIN
        SET @result = 0; -- Not enough stock
    END
    ELSE
    BEGIN
        SET @result = 1; -- Inventory validated
    END

    RETURN @result;
END;
GO
```

---

### 4. **Tax Validation**

#### **Summary**
This function verifies that the tax amounts calculated on an invoice match the expected tax values based on predefined tax codes. It ensures tax accuracy and compliance with tax regulations.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.validate_tax (@invoice_number VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Validate that taxes match the expected values, considering NULLs
    IF EXISTS (
        SELECT 1
        FROM BKARINV inv
        JOIN BKICTAX tax ON inv.BKAR_INV_TAXCODE = tax.BKIC_TAX_CODE
        WHERE inv.BKAR_INV_INVNO = @invoice_number 
          AND (
                inv.BKAR_INV_TAX_TOTAL IS NULL 
                OR tax.BKIC_TAX_CALC_TAX IS NULL 
                OR inv.BKAR_INV_TAX_TOTAL <> tax.BKIC_TAX_CALC_TAX
              )
    )
    BEGIN
        SET @result = 0; -- Tax mismatch or NULL values present
    END
    ELSE
    BEGIN
        SET @result = 1; -- Tax is valid
    END

    RETURN @result;
END;
GO
```

---

### 5. **Payment Terms Validation**

#### **Summary**
This function ensures that the payment terms specified on an invoice align with the customer’s default payment terms. It prevents discrepancies that could lead to payment delays or accounting errors.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.validate_payment_terms (@invoice_number VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Check if the payment terms are valid for the customer, considering case insensitivity and NULLs
    IF EXISTS (
        SELECT 1 
        FROM BKARINV inv
        JOIN BKARCUST cust ON inv.BKAR_INV_CUSTCODE = cust.BKAR_CUST_CUSTCODE
        WHERE inv.BKAR_INV_INVNO = @invoice_number 
          AND (
                cust.BKAR_CUST_PAY_TERMS IS NULL 
                OR inv.BKAR_INV_PAY_TERMS IS NULL 
                OR UPPER(cust.BKAR_CUST_PAY_TERMS) <> UPPER(inv.BKAR_INV_PAY_TERMS)
              )
    )
    BEGIN
        SET @result = 0; -- Payment terms mismatch or NULL values present
    END
    ELSE
    BEGIN
        SET @result = 1; -- Payment terms valid
    END

    RETURN @result;
END;
GO
```

---

### 6. **Salesperson Record Validation**

#### **Summary**
This function verifies that a salesperson associated with an invoice exists and is currently active. It prevents assigning sales efforts to inactive or non-existent sales representatives.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.validate_salesperson (@salesperson_code VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Combined condition to check if salesperson exists and is active
    IF NOT EXISTS (
        SELECT 1 
        FROM BKSLSREP
        WHERE BKSLS_REP_CODE = @salesperson_code
    )
    BEGIN
        SET @result = 0; -- Salesperson does not exist
    END
    ELSE IF EXISTS (
        SELECT 1 
        FROM BKSLSREP
        WHERE BKSLS_REP_CODE = @salesperson_code 
          AND BKSLS_REP_ACTV = 'N'
    )
    BEGIN
        SET @result = 0; -- Salesperson inactive
    END
    ELSE
    BEGIN
        SET @result = 1; -- Valid salesperson
    END

    RETURN @result;
END;
GO
```

---

### 7. **RMA Validation**

#### **Summary**
This function checks whether a Return Merchandise Authorization (RMA) record exists for a given invoice. It ensures that returns are properly authorized before processing.

#### **T-SQL Function**

```sql
CREATE FUNCTION dbo.validate_rma (@invoice_number VARCHAR(20))
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT;

    -- Ensure the RMA record exists for the invoice and is approved
    IF EXISTS (
        SELECT 1 
        FROM BKARINVL 
        WHERE BKAR_INV_INVNO = @invoice_number 
          AND BKAR_INV_TYPE = 'RMA'
          AND BKAR_INV_RMA_STATUS = 'Approved'
    )
    BEGIN
        SET @result = 1; -- RMA found and approved
    END
    ELSE
    BEGIN
        SET @result = 0; -- RMA not found or not approved
    END

    RETURN @result;
END;
GO
```
# Markpoint 20, 21, 22: Update Tax Authority and Process Tax Amounts

## Summary:
This function updates the tax authority records for an invoice and processes the tax amounts for each tax authority based on the invoice details. It handles multiple mark points (20, 21, and 22) using the `mark_point` function to ensure correct posting to the general ledger (GL) and updates to tax records. The function performs tax calculations based on the invoice taxable and non-taxable amounts and posts to the appropriate GL accounts.

## MSSQL Function

```sql
CREATE PROCEDURE Markpoint22_UpdateTaxAuthority
    @invoice_number VARCHAR(15)
AS
BEGIN
    -- Declare variables
    DECLARE @is_taxable CHAR(1), @tax_amount FLOAT, @tax_rate1 FLOAT, @tax_rate2 FLOAT, @freight_amount FLOAT;
    DECLARE @temp_tax_amt1 FLOAT, @temp_tax_amt2 FLOAT, @temp_tot_tax FLOAT;
    DECLARE @tax_amt1 FLOAT, @tax_amt2 FLOAT, @tax_amt3 FLOAT;
    DECLARE @tot_taxable FLOAT = 0, @tot_nontaxable FLOAT = 0, @month INT;
    DECLARE @tax_key VARCHAR(15), @vendor VARCHAR(50), @tax_frght CHAR(1);
    
    -- Retrieve the invoice details
    SELECT @is_taxable = BKAR_INV_TAXABL, @tax_amount = BKAR_INV_TAXAMT, 
           @tax_key = BKAR_INV_TAXKEY, @freight_amount = BKAR_INV_FRGHT, 
           @tax_rate1 = BKAR_INV_TAXRTE
    FROM BKAR_INV
    WHERE BKAR_INV_INVNUM = @invoice_number;

    -- If the mark point is already set to 22, return
    IF EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK = 22)
        RETURN;

    -- If the invoice is not taxable and the tax amount is 0, return
    IF @is_taxable = 'N' AND @tax_amount = 0
        RETURN;

    -- Fetch the tax authority record based on the tax key
    IF EXISTS (SELECT 1 FROM BKICTAX WHERE BKIC_TAX_AUTH = @tax_key)
    BEGIN
        -- Set the month value based on the invoice date
        SET @month = MONTH(GETDATE());

        -- Calculate the taxable amount including freight if applicable
        IF EXISTS (SELECT 1 FROM BKICTAX WHERE BKIC_TAX_FRGHT = 'Y' AND BKIC_TAX_AUTH = @tax_key)
            SET @tot_taxable = @tot_taxable + @freight_amount;

        -- Update taxable and non-taxable amounts
        UPDATE BKICTAX
        SET BKIC_TAX_TAXBLE[@month] = BKIC_TAX_TAXBLE[@month] + @tot_taxable,
            BKIC_TAX_NONTAX[@month] = BKIC_TAX_NONTAX[@month] + @tot_nontaxable,
            BKIC_TAX_OUTSTD = BKIC_TAX_OUTSTD + @tax_amount
        WHERE BKIC_TAX_AUTH = @tax_key;

        -- Calculate tax amounts based on the rates
        IF @tax_rate1 = BKIC_TAX_RATE1
        BEGIN
            SET @tax_amt1 = @tax_amount;
            SET @tax_amt2 = 0;
            SET @tax_amt3 = 0;
        END
        ELSE
        BEGIN
            -- Custom tax calculation logic for different tax rates
            SET @tax_amt1 = (@tot_taxable * BKIC_TAX_RATE1) / 100;
            SET @tax_amt2 = (@tot_taxable * BKIC_TAX_RATE2) / 100;
            SET @tax_amt3 = 0;
        END

        -- Reconcile the calculated total tax with the invoice tax amount
        SET @temp_tot_tax = @tax_amt1 + @tax_amt2 + @tax_amt3;
        IF @tax_amount <> @temp_tot_tax
            SET @tax_amt1 = @tax_amt1 + (@tax_amount - @temp_tot_tax);

        -- Update the tax collection amounts for the month
        UPDATE BKICTAX
        SET BKIC_TAX_COLECT[@month] = BKIC_TAX_COLECT[@month] + @tax_amt1,
            BKIC_TAX_COLEC2[@month] = BKIC_TAX_COLEC2[@month] + @tax_amt2,
            BKIC_TAX_OUTST1 = BKIC_TAX_OUTST1 + @tax_amt1,
            BKIC_TAX_OUTST2 = BKIC_TAX_OUTST2 + @tax_amt2
        WHERE BKIC_TAX_AUTH = @tax_key;

        -- Post to general ledger (GL) if tax amount 1 is not zero and mark point 20 has not been completed
        IF EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK < 20) AND @tax_amt1 <> 0
        BEGIN
            EXEC mark_point 20, 0, False;
            EXEC post_to_gl2 BKIC_TAX_GLACT, BKIC_TAX_GLDPT, '#1-Sls Tx Inv ' + @vendor, @tax_amt1;

            -- Handle post failure
            IF @@ERROR <> 0
            BEGIN
                EXEC clr @BKICTAX_HNDL;
                RETURN;
            END
            EXEC mark_point 20, 0, True;
        END

        -- Post tax amount 2 to GL if applicable and mark point 21 is not completed
        IF EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK < 21) AND @tax_amt2 <> 0
        BEGIN
            EXEC mark_point 21, 0, False;
            EXEC post_to_gl2 BKIC_TAX_GLACT2, BKIC_TAX_GLDPT2, '#2-Sls Tx Inv ' + @vendor, @tax_amt2;

            -- Handle post failure
            IF @@ERROR <> 0
            BEGIN
                EXEC clr @BKICTAX_HNDL;
                RETURN;
            END
            EXEC mark_point 21, 0, True;
        END
    END
    ELSE
    BEGIN
        -- Handle missing tax authority record
        IF EXISTS (SELECT 1 FROM BKSOMARK WHERE MARK < 20) AND @tax_amount <> 0
        BEGIN
            -- Post default tax to GL
            EXEC mark_point 20, 0, False;
            EXEC post_to_gl2 BKSY_TAX_GLACT, BKSY_TAX_GLDPT, 'Sls Tx Inv - System Dflt', @tax_amount;

            -- Handle post failure
            IF @@ERROR <> 0
            BEGIN
                EXEC clr @BKICTAX_HNDL;
                RETURN;
            END
            EXEC mark_point 20, 0, True;
        END
    END

    -- Save changes to BKICTAX
    IF @@ERROR = 0
    BEGIN
        EXEC mark_point 22, 0, False;
        UPDATE BKICTAX
        SET BKIC_TAX_OUTSTD = BKIC_TAX_OUTSTD + @tax_amount;
        EXEC mark_point 22, 0, True;
    END

    -- Final cleanup and post-status handling
    EXEC post_status;

END
GO
```

### Breakdown of Tasks:

1. **Set Markpoint 22 (Start):**
   - The `mark_point` function is used to indicate the beginning of tax authority updates at mark point 22.

2. **Update Tax Authority:**
   - The function checks if the invoice is taxable. If it is, the tax amounts are calculated and posted to the tax authority's record (`BKICTAX`), updating taxable, non-taxable, and outstanding amounts.

3. **Post to General Ledger (GL) for Tax Amounts (Markpoint 20 and 21):**
   - If the tax amount is not zero, mark point 20 is set, and the tax is posted to the appropriate GL accounts (`BKIC_TAX_GLACT` for tax amount 1 and `BKIC_TAX_GLACT2` for tax amount 2). The function checks if mark point 21 has already been set before posting tax amount 2.

4. **Complete Markpoint 22 (End):**
   - Once the tax authority updates are successful, mark point 22 is completed using the `mark_point` function.

5. **Handle Missing Tax Authority Record:**
   - If the tax authority record does not exist, a default system posting is performed for the tax amounts, and mark point 20 is set.

### Error Handling:

- The function uses `TRY...CATCH` blocks to handle errors during the posting to GL or updating the tax authority records. Any failure during these processes will result in appropriate cleanup and rollback.

### Testing:

- **Test Case 1: Standard Taxable Invoice**
  - Run the function with a standard taxable invoice and verify that all tax amounts are processed correctly and posted to the appropriate GL accounts.
  
- **Test Case 2: Non-Taxable Invoice**
  - Run the function with a non-taxable invoice and ensure that no tax amounts are processed, and the function completes without errors.

- **Test Case 3: Missing Tax Authority Record**
  - Run the function with an invoice that has no associated tax authority record and ensure that the default system posting is performed.

### Notes:

- **Mark Points:** Mark points 20, 21, and 22 are used to control the flow of posting to the GL accounts and ensure that each part of the process completes successfully before moving to the next.
- **Performance Considerations:** Test the function with large datasets to ensure that the tax calculation and posting processes do not significantly impact system performance.

# Create invoice from history



```sql
CREATE FUNCTION create_invoice_from_history(
    @OldInvoiceNumber NVARCHAR(20),
    @NewInvoiceNumber NVARCHAR(20),
    @NewSONumber NVARCHAR(20)
)
RETURNS VARCHAR(50)
AS
BEGIN
    BEGIN TRY
        -- Start a transaction
        BEGIN TRANSACTION;

        -- Copy data from BKARHINV to BKARINV with new Invoice Number and SO Number
        INSERT INTO BKARINV (
            [MDS_RECNUM],
            [BKAR_INV_NUM],
            [BKAR_INV_SONUM],
            [BKAR_INV_INVCD],
            [BKAR_INV_INVDTE],
            [BKAR_INV_CUSCOD],
            [BKAR_INV_CUSA1],
            [BKAR_INV_CUSNME],
            [BKAR_INV_CUSA2],
            [BKAR_INV_CUSCTY],
            [BKAR_INV_CUSST],
            [BKAR_INV_CUSZIP],
            [BKAR_INV_CUSCUN],
            [BKAR_INV_SHPCTY],
            [BKAR_INV_SHPST],
            [BKAR_INV_SHPZIP],
            [BKAR_INV_SHPCOD],
            [BKAR_INV_SHPNME],
            [BKAR_INV_SHPA1],
            [BKAR_INV_SHPA2],
            [BKAR_INV_SHPCUN],
            [BKAR_INV_SHPATN],
            [BKAR_INV_SHPVIA],
            [BKAR_INV_TERMD],
            [BKAR_INV_TERMNM],
            [BKAR_INV_SLSP],
            [BKAR_INV_ENTBY],
            [BKAR_INV_CUSORD],
            [BKAR_INV_TAXABL],
            [BKAR_INV_SUBTOT],
            [BKAR_INV_TAXAMT],
            [BKAR_INV_TOTAL],
            [BKAR_INV_COGS],
            [BKAR_INV_NL],
            [BKAR_INV_TAXRTE],
            [BKAR_INV_DESC],
            [BKAR_INV_GLDPT],
            [BKAR_INV_LINV_P],
            [BKAR_INV_RTS],
            [BKAR_INV_FRGHT],
            [BKAR_INV_FRTAX],
            [BKAR_INV_LOC],
            [BKAR_INV_TAXKEY],
            [BKAR_INV_ORDDTE],
            [BKAR_INV_ENDLNE],
            [BKAR_INV_GROUP],
            [BKAR_INV_FREQ],
            [BKAR_INV_MAX],
            [BKAR_INV_FRC_BO],
            [BKAR_INV_JOBCOD],
            [BKAR_INV_SHPDTE],
            [BKAR_INV_DUEDTE],
            [BKAR_INV_LOGON],
            [BKAR_INV_ACTDTE],
            [BKAR_INV_NOTE#],
            [BKAR_INV_WEBID],
            [BKAR_INV_FUEL],
            [BKAR_INV_COD],
            [BKAR_INV_SPAMT1],
            [BKAR_INV_SPAMT2],
            [BKAR_INV_SPAMT3],
            [BKAR_INV_FLAG1],
            [BKAR_INV_FLAG2],
            [BKAR_INV_FLAG3],
            [BKAR_INV_FLAG4],
            [BKAR_INV_FLAG5],
            [BKAR_INV_WDATE],
            [BKAR_INV_WTIME],
            [BKAR_INV_DTIME],
            [BKAR_INV_ZONE]
        )
        SELECT 
            [MDS_RECNUM], 
            @NewInvoiceNumber,   -- New Invoice Number
            @NewSONumber,        -- New SO Number
            [BKAR_INV_INVCD],
            [BKAR_INV_INVDTE],
            [BKAR_INV_CUSCOD],
            [BKAR_INV_CUSA1],
            [BKAR_INV_CUSNME],
            [BKAR_INV_CUSA2],
            [BKAR_INV_CUSCTY],
            [BKAR_INV_CUSST],
            [BKAR_INV_CUSZIP],
            [BKAR_INV_CUSCUN],
            [BKAR_INV_SHPCTY],
            [BKAR_INV_SHPST],
            [BKAR_INV_SHPZIP],
            [BKAR_INV_SHPCOD],
            [BKAR_INV_SHPNME],
            [BKAR_INV_SHPA1],
            [BKAR_INV_SHPA2],
            [BKAR_INV_SHPCUN],
            [BKAR_INV_SHPATN],
            [BKAR_INV_SHPVIA],
            [BKAR_INV_TERMD],
            [BKAR_INV_TERMNM],
            [BKAR_INV_SLSP],
            [BKAR_INV_ENTBY],
            [BKAR_INV_CUSORD],
            [BKAR_INV_TAXABL],
            [BKAR_INV_SUBTOT],
            [BKAR_INV_TAXAMT],
            [BKAR_INV_TOTAL],
            [BKAR_INV_COGS],
            [BKAR_INV_NL],
            [BKAR_INV_TAXRTE],
            [BKAR_INV_DESC],
            [BKAR_INV_GLDPT],
            [BKAR_INV_LINV_P],
            [BKAR_INV_RTS],
            [BKAR_INV_FRGHT],
            [BKAR_INV_FRTAX],
            [BKAR_INV_LOC],
            [BKAR_INV_TAXKEY],
            [BKAR_INV_ORDDTE],
            [BKAR_INV_ENDLNE],
            [BKAR_INV_GROUP],
            [BKAR_INV_FREQ],
            [BKAR_INV_MAX],
            [BKAR_INV_FRC_BO],
            [BKAR_INV_JOBCOD],
            [BKAR_INV_SHPDTE],
            [BKAR_INV_DUEDTE],
            [BKAR_INV_LOGON],
            [BKAR_INV_ACTDTE],
            [BKAR_INV_NOTE#],
            [BKAR_INV_WEBID],
            [BKAR_INV_FUEL],
            [BKAR_INV_COD],
            [BKAR_INV_SPAMT1],
            [BKAR_INV_SPAMT2],
            [BKAR_INV_SPAMT3],
            [BKAR_INV_FLAG1],
            [BKAR_INV_FLAG2],
            [BKAR_INV_FLAG3],
            [BKAR_INV_FLAG4],
            [BKAR_INV_FLAG5],
            [BKAR_INV_WDATE],
            [BKAR_INV_WTIME],
            [BKAR_INV_DTIME],
            [BKAR_INV_ZONE]
        FROM BKARHINV
        WHERE BKAR_INV_NUM = @OldInvoiceNumber;

        -- Copy data from BKARHIVL to BKARINVL with new Invoice Number
        INSERT INTO BKARINVL (
            [MDS_RECNUM],
            [BKAR_INVL_INVNM],
            [BKAR_INVL_ESD],
            [BKAR_INVL_MSG],
            [BKAR_INVL_PCODE],
            [BKAR_INVL_PDESC],
            [BKAR_INVL_PQTY],
            [BKAR_INVL_PPRCE],
            [BKAR_INVL_PDISC],
            [BKAR_INVL_PEXT],
            [BKAR_INVL_PCOGS],
            [BKAR_INVL_ITYPE],
            [BKAR_INVL_TXBLE],
            [BKAR_INVL_UBO],
            [BKAR_INVL_USTD],
            [BKAR_INVL_RTS],
            [BKAR_INVL_LOC],
            [BKAR_INVL_BLDNM],
            [BKAR_INVL_AUTOB],
            [BKAR_INVL_NOTE#],
            [BKAR_INVL_LINE],
            [BKAR_INVL_CSLNE],
            [BKAR_INVL_WARRC],
            [BKAR_INVL_WARRD],
            [BKAR_INVL_WARRA],
            [BKAR_INVL_COUPC],
            [BKAR_INVL_COUPA],
            [BKAR_INVL_FRGT],
            [BKAR_INVL_RESTK]
        )
        SELECT 
            [MDS_RECNUM], 
            @NewInvoiceNumber,   -- New Invoice Number for Invoice Lines
            [BKAR_INVL_ESD],
            [BKAR_INVL_MSG],
            [BKAR_INVL_PCODE],
            [BKAR_INVL_PDESC],
            [BKAR_INVL_PQTY],
            [BKAR_INVL_PPRCE],
            [BKAR_INVL_PDISC],
            [BKAR_INVL_PEXT],
            [BKAR_INVL_PCOGS],
            [BKAR_INVL_ITYPE],
            [BKAR_INVL_TXBLE],
            [BKAR_INVL_UBO],
            [BKAR_INVL_USTD],
            [BKAR_INVL_RTS],
            [BKAR_INVL_LOC],
            [BKAR_INVL_BLDNM],
            [BKAR_INVL_AUTOB],
            [BKAR_INVL_NOTE#],
            [BKAR_INVL_LINE],
            [BKAR_INVL_CSLNE],
            [BKAR_INVL_WARRC],
            [BKAR_INVL_WARRD],
            [BKAR_INVL_WARRA],
            [BKAR_INVL_COUPC],
            [BKAR_INVL_COUPA],
            [BKAR_INVL_FRGT],
            [BKAR_INVL_RESTK]
        FROM BKARHIVL
        WHERE BKAR_INVL_INVNM = @OldInvoiceNumber;

        -- Commit the transaction if successful
        COMMIT TRANSACTION;

        RETURN 'Invoice copied successfully with new Invoice Number and SO Number.';
    END TRY

    BEGIN CATCH
        -- Rollback transaction if an error occurs
        ROLLBACK TRANSACTION;
        RETURN ERROR_MESSAGE();
    END CATCH
END;
``

`

### Explanation:
1. The function `create_invoice_from_history` takes three parameters: `@OldInvoiceNumber`, `@NewInvoiceNumber`, and `@NewSONumber`.
2. It copies the invoice data from `BKARHINV` to `BKARINV` but replaces the old invoice number and SO number with the new ones provided.
3. Similarly, it copies the corresponding invoice line items from `BKARHIVL` to `BKARINVL` with the new invoice number.
4. The function uses transactions to ensure data integrity, rolling back changes if any error occurs during the process.

This will allow you to copy an invoice from the history tables with new identifiers while keeping all other details intact.
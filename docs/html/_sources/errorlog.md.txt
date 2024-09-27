# Error Log
-- =============================================
-- Author:        Chris Watkins
-- Create date:   YYYY-MM-DD
-- Description:   Table to Log Errors from Stored Procedures with Invoice Number and Mark Point
-- =============================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[_PostingErrorLog]') AND type in (N'U'))
BEGIN
    CREATE TABLE dbo._PostingErrorLog (
        ErrorID INT IDENTITY(1,1) PRIMARY KEY,
        InvoiceNumber INT NOT NULL,
        MarkPoint INT NULL,
        ErrorMessage NVARCHAR(4000) NOT NULL,
        ErrorSeverity INT NOT NULL,
        ErrorState INT NOT NULL,
        ErrorTime DATETIME NOT NULL DEFAULT GETDATE()
    );
END;
GO

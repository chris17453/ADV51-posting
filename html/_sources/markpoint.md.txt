# `mark_point` Stored Procedure

## **Summary**

The `mark_point` stored procedure is responsible for logging specific checkpoints (mark points) during the sales order posting process into the `BKSOMARK` table. Each mark point records essential information, including the mark point identifier, line number, execution status (success or failure), and timestamp. To maintain data integrity and ensure that mark points are logged in the correct sequence, the procedure employs robust transaction management and locking mechanisms. This comprehensive logging facilitates accurate auditing, monitoring, and troubleshooting of the sales order workflow.

## **BKSOMARK Table Structure**

Understanding the structure of the `BKSOMARK` table is crucial for implementing the `mark_point` procedure effectively. Below is the schema based on the provided information:

- **MDS_RECNUM**: Primary key, likely an auto-incrementing integer.
- **BKSOMARK_INVNM**: Invoice Number (`INT`).
- **BKSOMARK_MARK**: Mark Point Identifier (`INT`).
- **BKSOMARK_LINE**: Line Number within the Invoice (`FLOAT`).
- **BKSOMARK_DONE**: Execution Status (`SMALLINT`) — `1` for success, `0` for failure.
- **BKSOMARK_DATE**: Date of the Mark Point (`DATE`).


## **T-SQL Procedure**

Below is the implementation of the `mark_point` stored procedure, incorporating transaction management and locking to ensure sequential logging of mark points.

```sql
-- =============================================
-- Author:        Chris Watkins of Watkins Labs
-- Create date:   YYYY-MM-DD
-- Description:   Log Mark Points into BKSOMARK Table with Transaction and Locking
-- =============================================

CREATE PROCEDURE dbo.mark_point (
    @invoiceNum INT,
    @mark_point INT,
    @line_num FLOAT,
    @pass_done SMALLINT
)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- =============================
        -- Transaction Management
        -- =============================

        -- Set the isolation level to SERIALIZABLE to prevent phantom reads
        SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
        BEGIN TRANSACTION;

        -- =============================
        -- Parameter Validation
        -- =============================

        -- Validate @invoiceNum (must be a positive integer)
        IF @invoiceNum <= 0
        BEGIN
            RAISERROR('Invoice number must be a positive integer.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Validate @mark_point (must be a positive integer)
        IF @mark_point <= 0
        BEGIN
            RAISERROR('Mark point identifier must be a positive integer.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Validate @line_num (must be a positive number)
        IF @line_num <= 0
        BEGIN
            RAISERROR('Line number must be a positive number.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Validate @pass_done (must be either 0 or 1)
        IF @pass_done NOT IN (0, 1)
        BEGIN
            RAISERROR('Pass done must be either 0 (False) or 1 (True).', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- =============================
        -- Locking Mechanism
        -- =============================

        -- Acquire an exclusive lock on the BKSOMARK row for the specific invoice
        -- This ensures that no other transactions can insert or modify mark points for the same invoice concurrently
        DECLARE @dummy INT;
        SELECT @dummy = 1
        FROM BKSOMARK WITH (UPDLOCK, HOLDLOCK)
        WHERE BKSOMARK_INVNM = @invoiceNum;

        -- =============================
        -- Sequential Mark Point Logging
        -- =============================

        -- Retrieve the current maximum mark point for the invoice
        DECLARE @current_max_mark INT;
        SELECT @current_max_mark = MAX(BKSOMARK_MARK)
        FROM BKSOMARK
        WHERE BKSOMARK_INVNM = @invoiceNum;

        -- Ensure that the new mark_point is greater than the current maximum to maintain order
        IF @current_max_mark IS NOT NULL AND @mark_point <= @current_max_mark
        BEGIN
            RAISERROR('Mark point identifier must be greater than the existing maximum mark point for the invoice.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- =============================
        -- Insert or Update Mark Point
        -- =============================

        IF EXISTS (
            SELECT 1 
            FROM BKSOMARK
            WHERE BKSOMARK_INVNM = @invoiceNum
        )
        BEGIN
            -- Update existing row with the new mark point
            UPDATE BKSOMARK
            SET 
                BKSOMARK_MARK = @mark_point,
                BKSOMARK_LINE = @line_num,
                BKSOMARK_DONE = @pass_done,
                BKSOMARK_DATE = CAST(GETDATE() AS DATE)
            WHERE 
                BKSOMARK_INVNM = @invoiceNum;
        END
        ELSE
        BEGIN
            -- Insert a new row if it does not exist
            INSERT INTO BKSOMARK (
                BKSOMARK_INVNM,
                BKSOMARK_MARK,
                BKSOMARK_LINE,
                BKSOMARK_DONE,
                BKSOMARK_DATE
            )
            VALUES (
                @invoiceNum,
                @mark_point,
                @line_num,
                @pass_done,
                CAST(GETDATE() AS DATE)
            );
        END

        -- =============================
        -- Commit Transaction
        -- =============================

        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        -- =============================
        -- Error Handling
        -- =============================

        -- Rollback the transaction if it's still active
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        -- Retrieve error information
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        -- Optionally, log the error to an ErrorLog table
        -- Uncomment and modify the following lines if an ErrorLog table exists
        /*
        INSERT INTO dbo.ErrorLog (ErrorMessage, ErrorSeverity, ErrorState, ErrorTime)
        VALUES (@ErrorMessage, @ErrorSeverity, @ErrorState, GETDATE());
        */

        -- Re-raise the error to the calling environment
        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END;
GO
```

## **Detailed Breakdown of Actions**

1. **Parameter Definitions:**
   - `@invoiceNum INT`: The invoice number associated with the sales order.
   - `@mark_point INT`: The identifier for the specific mark point being logged.
   - `@line_num FLOAT`: The line number within the invoice where the mark point is being logged.
   - `@pass_done SMALLINT`: A boolean indicating the success (`1`) or failure (`0`) of the mark point.

2. **Transaction Management:**
   - **Isolation Level:** Set to `SERIALIZABLE` to prevent phantom reads and ensure complete isolation from other transactions.
   - **Transaction Start:** Begins a transaction to encapsulate all operations, ensuring atomicity.

3. **Parameter Validation:**
   - **Invoice Number (`@invoiceNum`):** Must be a positive integer.
   - **Mark Point Identifier (`@mark_point`):** Must be a positive integer.
   - **Line Number (`@line_num`):** Must be a positive number.
   - **Pass Done (`@pass_done`):** Must be either `0` (False) or `1` (True).

4. **Locking Mechanism:**
   - **Purpose:** Prevents concurrent transactions from inserting or modifying mark points for the same invoice, ensuring that mark points are logged in the correct sequence.
   - **Implementation:** Uses table hints `UPDLOCK` and `HOLDLOCK` in a dummy `SELECT` statement to acquire an exclusive lock on the relevant rows.
   - **Dummy Variable:** `@dummy INT` is used to store the result of the `SELECT` statement, which serves solely to acquire the lock.

5. **Sequential Mark Point Logging:**
   - **Purpose:** Ensures that each new mark point is sequentially higher than the existing maximum mark point for the invoice.
   - **Implementation:** Retrieves the current maximum `BKSOMARK_MARK` for the invoice and validates that the new `@mark_point` is greater.

6. **Insert or Update Mark Point:**
   - **Action:** 
     - **Update Existing Row:** If a row for the invoice already exists, update it with the new mark point details.
     - **Insert New Row:** If no row exists for the invoice, insert a new record with the provided mark point details.
   - **Fields Updated/Inserted:**
     - `BKSOMARK_MARK`: Mark Point Identifier.
     - `BKSOMARK_LINE`: Line Number.
     - `BKSOMARK_DONE`: Execution Status.
     - `BKSOMARK_DATE`: Current Date (`CAST(GETDATE() AS DATE)`).

7. **Transaction Commit:**
   - **Action:** Commits the transaction, making all changes permanent.

8. **Error Handling with TRY...CATCH:**
   - **TRY Block:** Contains the main logic, including transaction management, parameter validation, locking, and data insertion/updating.
   - **CATCH Block:** 
     - **Rollback:** Rolls back the transaction if it's still active.
     - **Error Retrieval:** Captures error details using `ERROR_MESSAGE()`, `ERROR_SEVERITY()`, and `ERROR_STATE()`.
     - **Optional Error Logging:** Provides commented-out code to log errors into an `ErrorLog` table if such a table exists.
     - **Error Raising:** Re-raises the error to the calling environment using `RAISERROR`.

## **Recommendations**

1. **Input Validation Enhancements:**
   - **Sanitization:** While parameters are strongly typed, additional checks can be implemented to ensure data integrity.
     ```sql
     -- Example: Ensure @invoiceNum contains only digits
     IF PATINDEX('%[^0-9]%', CAST(@invoiceNum AS VARCHAR)) > 0
     BEGIN
         RAISERROR('Invalid characters in Invoice Number.', 16, 1);
         ROLLBACK TRANSACTION;
         RETURN;
     END
     ```

2. **Indexing:**
   - **Performance Optimization:** Create indexes on columns frequently used in queries to enhance performance.
     ```sql
     CREATE INDEX IDX_BKSOMARK_INVNM ON BKSOMARK (BKSOMARK_INVNM);
     CREATE INDEX IDX_BKSOMARK_MARK ON BKSOMARK (BKSOMARK_MARK);
     CREATE INDEX IDX_BKSOMARK_LINE ON BKSOMARK (BKSOMARK_LINE);
     ```
   - **Benefits:** Improves the speed of data retrieval operations, especially for large datasets.

3. **Error Logging Enhancements:**
   - **Purpose:** Maintain a persistent record of errors for auditing and troubleshooting.
   - **Implementation:**
     - **Create an `ErrorLog` Table:**
       ```sql
       CREATE TABLE dbo.ErrorLog (
           ErrorID INT IDENTITY(1,1) PRIMARY KEY,
           ErrorMessage NVARCHAR(4000),
           ErrorSeverity INT,
           ErrorState INT,
           ErrorTime DATETIME DEFAULT GETDATE()
       );
       ```
     - **Log Errors in the CATCH Block:**
       ```sql
       INSERT INTO dbo.ErrorLog (ErrorMessage, ErrorSeverity, ErrorState)
       VALUES (@ErrorMessage, @ErrorSeverity, @ErrorState);
       ```
     - **Enable Error Logging:** Uncomment the relevant lines in the CATCH block to activate error logging.

4. **Security Considerations:**
   - **Permissions:** Restrict execute permissions on the `mark_point` procedure to authorized roles only.
     ```sql
     GRANT EXECUTE ON dbo.mark_point TO [SalesProcessorRole];
     ```
   - **Least Privilege:** Ensure that users executing the procedure have only the necessary permissions to perform required operations on the `BKSOMARK` table.

5. **Performance Optimization:**
   - **Batch Inserts:** If multiple mark points need to be logged simultaneously, consider batching insert operations to reduce transaction overhead.
   - **Set-Based Operations:** Utilize set-based operations instead of row-by-row processing where feasible to enhance performance.

6. **Concurrency Control:**
   - **Isolation Levels:** Using `SERIALIZABLE` isolation level ensures complete isolation from other transactions, preventing race conditions and maintaining data consistency.
   - **Locking Hints:** Employing `UPDLOCK` and `HOLDLOCK` in the `SELECT` statement acquires an exclusive lock on the relevant rows, ensuring that no other transactions can modify them until the current transaction is complete.

7. **Idempotency:**
   - **Design Consideration:** Ensure that re-executing the `mark_point` procedure with the same parameters does not result in duplicate entries.
   - **Implementation Suggestion:**
     ```sql
     IF NOT EXISTS (
         SELECT 1 
         FROM BKSOMARK
         WHERE BKSOMARK_INVNM = @invoiceNum
           AND BKSOMARK_MARK = @mark_point
           AND BKSOMARK_LINE = @line_num
     )
     BEGIN
         INSERT INTO BKSOMARK (
             BKSOMARK_INVNM,
             BKSOMARK_MARK,
             BKSOMARK_LINE,
             BKSOMARK_DONE,
             BKSOMARK_DATE
         )
         VALUES (
             @invoiceNum,
             @mark_point,
             @line_num,
             @pass_done,
             CAST(GETDATE() AS DATE)
         );
     END
     ELSE
     BEGIN
         -- Optionally, update the existing record if needed
         UPDATE BKSOMARK
         SET 
             BKSOMARK_DONE = @pass_done,
             BKSOMARK_DATE = CAST(GETDATE() AS DATE)
         WHERE 
             BKSOMARK_INVNM = @invoiceNum
             AND BKSOMARK_MARK = @mark_point
             AND BKSOMARK_LINE = @line_num;
     END
     ```

8. **Documentation:**
   - **Clarity:** Maintain clear and comprehensive documentation within the procedure to facilitate future maintenance and onboarding of new team members.
   - **Comments:** Use inline comments to explain complex logic or business rules implemented within the procedure.

9. **Extensibility:**
   - **Future Fields:** If the `BKSOMARK` table is updated to include additional fields in the future, update the `mark_point` procedure accordingly to capture and log the new information.

## **Testing Guidelines**

1. **Unit Testing:**
   - **Objective:** Validate each component of the procedure individually.
   - **Test Cases:**
     - **Valid Inputs:**
       - `@invoiceNum` exists in `BKARINV`.
       - Valid `@mark_point` and `@line_num` values.
       - `@pass_done` set to `1` (success) and `0` (failure).
     - **Invalid Inputs:**
       - `@invoiceNum` is a negative integer or zero.
       - `@mark_point` or `@line_num` are non-positive.
       - `@pass_done` is neither `0` nor `1`.

2. **Integration Testing:**
   - **Objective:** Ensure that the procedure interacts correctly with other system components.
   - **Test Cases:**
     - Execute the procedure within the `post_so` workflow and verify that mark points are logged accurately.
     - Simulate concurrent executions to test concurrency controls.

3. **Error Handling Testing:**
   - **Objective:** Confirm that errors are handled gracefully without leaving the system in an inconsistent state.
   - **Test Cases:**
     - Provide invalid parameters to trigger errors.
     - Simulate failures in dependent tables or procedures.

4. **Performance Testing:**
   - **Objective:** Assess the procedure’s performance under various loads.
   - **Test Cases:**
     - Execute the procedure with a large number of mark points to evaluate scalability.
     - Monitor execution time and resource utilization.

5. **Security Testing:**
   - **Objective:** Ensure that the procedure is secure against unauthorized access and SQL injection.
   - **Test Cases:**
     - Attempt to execute the procedure with unauthorized roles.
     - Provide malicious input to test input validation.

6. **Regression Testing:**
   - **Objective:** Verify that new changes do not adversely affect existing functionalities.
   - **Test Cases:**
     - Re-run previous test cases after making modifications to ensure consistent behavior.

## **Example Usage**

To execute the `mark_point` stored procedure, use the following command, replacing the placeholders with actual values:

```sql
EXEC dbo.mark_point 
    @invoiceNum = 123456, 
    @mark_point = 3, 
    @line_num = 1.0, 
    @pass_done = 1;
```

## **Maintenance and Future Enhancements**

1. **Procedure Modularity:**
   - **Design Principle:** Keep the procedure modular to facilitate easier maintenance and potential reuse in other processes.
   - **Implementation:** Ensure that each mark point corresponds to a specific and distinct aspect of the sales order processing.

2. **Logging Enhancements:**
   - **Detailed Logs:** Enhance the logging mechanism to capture additional context or metadata as required.
   - **Audit Trails:** Maintain comprehensive audit trails for compliance and historical analysis.

3. **Regular Reviews:**
   - **Objective:** Periodically review and update the procedure to accommodate changes in business rules, system architecture, or compliance requirements.
   - **Action:** Schedule regular code reviews and updates in collaboration with the development and QA teams.

4. **Backup and Recovery:**
   - **Objective:** Ensure data integrity and availability by implementing robust backup and recovery strategies.
   - **Action:** Regularly back up the `BKSOMARK` table and related database components.

5. **Documentation Updates:**
   - **Objective:** Keep the documentation up-to-date with any changes made to the procedure.
   - **Action:** Implement a versioning system for documentation to track changes over time.

6. **Performance Monitoring:**
   - **Objective:** Continuously monitor the procedure’s performance to identify and address any bottlenecks.
   - **Action:** Use SQL Server’s monitoring tools to analyze execution plans and optimize queries as needed.

## **Conclusion**

The `mark_point` stored procedure is a pivotal component for logging and tracking the execution of various checkpoints during the sales order posting process. By adhering to best practices in its implementation, including comprehensive validation, robust error handling, and detailed logging with appropriate transaction management and locking mechanisms, this procedure ensures the integrity, reliability, and auditability of your sales order system.

**Key Benefits:**

- **Comprehensive Auditing:** Detailed logging of each mark point facilitates thorough auditing and tracking.
- **Data Integrity:** Rigorous validation steps ensure that only valid and consistent data is processed.
- **Error Resilience:** Robust error handling mechanisms prevent inconsistent states and facilitate troubleshooting.
- **Scalability:** Optimized for performance, allowing efficient processing of large volumes of sales orders.

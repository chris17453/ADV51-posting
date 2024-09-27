# Posting Database Tables Used 

| **Database Name** | **Table Name**   | **What It Does**                                               | **Read** | **Insert** | **Update** | **Delete** |
|-------------------|------------------|----------------------------------------------------------------|----------|------------|------------|------------|
| **ADVDATA**       | **BKCOUPON**      | Coupon tracking                                               | X        |            | X          |            |
| **ADVDATA**       | **BKEXCHNG**      | Exchange rates                                                | X        |            | X          |            |
| **ADVDATA**       | **BKICCAT**       | Item category master                                          | X        |            | X          |            |
| **ADVDATA**       | **BKMPLOCS**      | Mapping of locations                                          | X        |            | X          |            |
| **ADVDATA**       | **BKPRULES**      | Pricing rules                                                 | X        |            | X          |            |
| **ADVDATA**       | **BKSLSREP**      | Sales representative data                                     | X        |            | X          |            |
| **ADVDATA**       | **BKSLSTYP**      | Sales type classification                                     | X        |            | X          |            |
| **ADVDATA**       | **BKZIP**         | ZIP code details                                              | X        |            |            |            |
| **PACIFIC**       | **BKARCPRC**      | Customer pricing details                                      | X        |            | X          |            |
| **PACIFIC**       | **BKARCUST**      | Customer master data                                          | X        |            | X          |            |
| **PACIFIC**       | **BKARHINV**      | Invoice history header                                        | X        |            |            |            |
| **PACIFIC**       | **BKARHIVL**      | Invoice history line items                                    | X        |            |            |            |
| **PACIFIC**       | **BKARINV**       | Current invoice headers                                       | X        |            | X          | x          |
| **PACIFIC**       | **BKARINVL**      | Current invoice line items                                    | X        |            |            | X          |
| **PACIFIC**       | **BKARINVT**      | Invoice totals and summary                                    | X        |            | X          |            |
| **PACIFIC**       | **BKARLSTF**      | Invoice listing flags                                         | X        |            | X          |            |
| **PACIFIC**       | **BKARLSTS**      | Invoice listing summary                                       | X        |            | X          |            |
| **PACIFIC**       | **BKARPR**        | Customer points data                                          | X        |            | X          |            |
| **PACIFIC**       | **BKDEPDAY**      | Daily deposit records                                         | X        | X          |            |            |
| **PACIFIC**       | **BKGLCHK**       | Cash transaction logs                                         | X        | X          |            |            |
| **PACIFIC**       | **BKGLCOA**       | General ledger chart of accounts                              | X        |            | X          |            |
| **PACIFIC**       | **BKGLTRAN**      | General ledger transactions                                   | X        | X          |            |            |
| **PACIFIC**       | **BKHELP**        | Help documentation                                            | X        |            |            |            |
| **PACIFIC**       | **BKICLOC**       | Item location master                                          | X        |            | X          |            |
| **PACIFIC**       | **BKICLOCM**      | Item location details for movement                            | X        |            | X          |            |
| **PACIFIC**       | **BKICLOCW**      | Item location and warehouse data                              | X        |            | X          |            |
| **PACIFIC**       | **BKICLWTR**      | RMA (Return Merchandise Authorization) line details           | X        |            | X          |            |
| **PACIFIC**       | **BKICMSTR**      | Item master details                                           | X        |            | X          |            |
| **PACIFIC**       | **BKICTAX**       | Tax authority details                                         | X        |            | X          |            |
| **PACIFIC**       | **BKICTRAN**      | Item transaction history                                      | X        |            |            |            |
| **PACIFIC**       | **BKLOGGER**      | Logs for system and user activities                           | X        | X          |            |            |
| **PACIFIC**       | **BKPTSHST**      | Points history for customer loyalty programs                  | X        | X          |            |            |
| **PACIFIC**       | **BKRMAHST**      | RMA history                                                   | X        | X          |            |            |
| **PACIFIC**       | **BKSLSWEB**      | Web sales tracking                                            | X        | X          | X          |            |
| **PACIFIC**       | **BKSOBUCK**      | Sales buckets for customers                                   | X        | X          | X          |            |
| **PACIFIC**       | **BKSOLOCK**      | Sales order lock details                                      | X        |            | X          |            |
| **PACIFIC**       | **BKSOMARK**      | Mark points for tracking transaction progress                 | X        |            |            |            |
| **PACIFIC**       | **BKSOMKLG**      | Sales order marketing log                                     | X        | X          |            |            |
| **PACIFIC**       | **BKSONOTE**      | Sales order notes                                             | X        | X          |            |            |
| **PACIFIC**       | **BKSYCHCK**      | Check details for payment processing                          | X        |            |            |            |
| **PACIFIC**       | **BKSYMSTR**      | System master table                                           | X        |            | X          |            |
| **PACIFIC**       | **BKSYSSEC**      | System security settings                                      | X        |            | X          |            |
| **PACIFIC**       | **BKSYTERM**      | System terminal settings                                      | X        |            | X          |            |
| **PACIFIC**       | **BKSYUSER**      | User accounts                                                 | X        |            | X          |            |

                'BKGLTRNM',

## UNKNOWNS, the code opens these tables, but im not seeing the reference. possibly burried in another file
- BKARLSTS: 
- BKARLSTF: 
- BKARCPRC: 
- BKDEPDAY: 
- BKSLSTYP: 
- BKLOGGER: 

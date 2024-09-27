# Invoice Processing Logic
- This will process a single RMA or INVOICE

## Table of Contents

## Database
- [Database](./database.txt)


## POSTING
- [Posting function](./post_so.md) <--Main entrypoint


## Supporting functions
- [markpoint](./markpoint.md)
- [GL Posting fucntion](./post_to_gl2.md)
- [pre-valiation.md](./pre-valiation.md)

## Mark Points (Steps in posting)
- 1,2 [Update AR/Cust Records](./markpoint-1.md)
- 3 [Update Inventory Transactions](./markpoint-3.md)
- 4 [Post to Accounts Receivable or Cash Account](./markpoint-4.md)
- 5 [Post Freight Charges](./markpoint-5.md)
- 6 [Post Fuel Charges](./markpoint-6.md)
- 7 [Update Inventory Location](./markpoint-7.md) PER LINE ITEM
- 8 [Save to Inventory Location Warehouse (RMA)](./markpoint-8.md) PER LINE ITEM
- 9 [Update Inventory Master](./markpoint-9.md) PER LINE ITEM
- 10 [Post to Sales Account](./markpoint-10.md) PER LINE ITEM
- 11 [Post Restocking Fee (RMA)](./markpoint-11.md) PER LINE ITEM
- 12 [Post Expense](./markpoint-12.md) PER LINE ITEM
- 13 [Post Asset](./markpoint-13.md) PER LINE ITEM
- 14 [Save to Inventory Transaction](./markpoint-14.md) PER LINE ITEMrr
- 15 [Save Inventory Line Item](./markpoint-15.md) PER LINE ITEM
- 16 [Move Invoice Line Item to History](./markpoint-16.md) PER LINE ITEM
- 17 [Delete or Resave Invoice Line Item](./markpoint-17.md) PER LINE ITEM
- 18 [Save to Points History](./markpoint-18.md) 
- 19 [Save to Points Bucket](./markpoint-19.md)
- 20 ,21, 22 [Update Tax](./markpoint-20.md)
- 23 [Delete Remaining Invoice Line Items](./markpoint-23.md)
- 24 [Save to Sales Order Bucket](./markpoint-24.md)
- 25 [Copy Invoice Header to Historical Invoice](./markpoint-25.md)
- 26 [Delete or Resave Invoice Header](./markpoint-26.md)




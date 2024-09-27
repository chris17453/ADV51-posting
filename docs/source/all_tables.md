# All tables

Table: BKCOUPON
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BK_COUPON_NUM', 'data_type': 'varchar', 'max_length': 15, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BK_COUPON_AMT', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BK_COUPON_DESC', 'data_type': 'varchar', 'max_length': 30, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BK_COUPON_MDATE', 'data_type': 'date', 'max_length': 3, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BK_COUPON_MAILD', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BK_COUPON_EXP', 'data_type': 'date', 'max_length': 3, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKCOUPON__E1AC68A318DAF61C', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BK_COUPON_NUM']

Table: BKEXCHNG
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BKEXCHNG_DATE', 'data_type': 'date', 'max_length': 3, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKEXCHNG_RATE', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKEXCHNG_PRATE', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKEXCHNG_DSRATE', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKEXCHNG__E1AC68A364D393E7', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BKEXCHNG_DATE']

Table: BKICCAT
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BKIC_CAT_CAT', 'data_type': 'varchar', 'max_length': 4, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKIC_CAT_DESC', 'data_type': 'varchar', 'max_length': 30, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKIC_CAT_FMLY', 'data_type': 'varchar', 'max_length': 5, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKIC_CAT_TABLE', 'data_type': 'varchar', 'max_length': 8, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKICCAT__E1AC68A30CF5549A', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BKIC_CAT_CAT']

Table: BKMPLOCS
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BKMP_LOCS_LOC', 'data_type': 'varchar', 'max_length': 10, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKMP_LOCS_DESC', 'data_type': 'varchar', 'max_length': 30, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKMP_LOCS_SUB', 'data_type': 'varchar', 'max_length': 8, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKMP_LOCS_GLDPT', 'data_type': 'varchar', 'max_length': 4, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKMP_LOCS_ACTV', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKMP_LOCS_RADSH', 'data_type': 'varchar', 'max_length': 10, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKMPLOCS__E1AC68A314B39A7F', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BKMP_LOCS_LOC']

Table: BKPRULES
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BKPRULES_PLEVEL', 'data_type': 'varchar', 'max_length': 3, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_DESC', 'data_type': 'varchar', 'max_length': 25, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_SINGLE', 'data_type': 'varchar', 'max_length': 15, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_SINGLF', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_BDATEL', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_ZONEL', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_FLOOR', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_STOCK', 'data_type': 'varchar', 'max_length': 15, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_CONT', 'data_type': 'varchar', 'max_length': 15, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_LISTF', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_CANFAC', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_CANSUR', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_PTRATE', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_LIST', 'data_type': 'varchar', 'max_length': 15, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_LOCP', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_DSRATE', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_RNDSNP', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_RNDSTP', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_RNDLP', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_RNDBEL', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_WCDISC', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_WCMAX', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKPRULES_DISTPL', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKPRULES__E1AC68A3A43315DD', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BKPRULES_PLEVEL']

Table: BKSLSREP
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BKSLS_REP_CODE', 'data_type': 'int', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_NAME', 'data_type': 'varchar', 'max_length': 25, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_MGR', 'data_type': 'int', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_LOGIN', 'data_type': 'varchar', 'max_length': 15, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_TYPE', 'data_type': 'varchar', 'max_length': 2, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_EMAIL', 'data_type': 'varchar', 'max_length': 50, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_STDTE', 'data_type': 'date', 'max_length': 3, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_MAXCM', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_REP_WHLOC', 'data_type': 'varchar', 'max_length': 10, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKSLSREP__E1AC68A3182FD8FB', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BKSLS_REP_CODE']

Table: BKSLSTYP
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 1}
  - {'name': 'BKSLS_TYP_TYPE', 'data_type': 'varchar', 'max_length': 2, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKSLS_TYP_CLASS', 'data_type': 'varchar', 'max_length': 2, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': 'PK__BKSLSTYP__E1AC68A3DA5FAA0C', 'type': 'CLUSTERED', 'is_unique': True, 'columns': ['MDS_RECNUM']}
Lookup Keys: ['BKSLS_TYP_TYPE']

Table: BKZIP
Schema: dbo
Database: ADVDATA
Columns:
  - {'name': 'MDS_RECNUM', 'data_type': 'decimal', 'max_length': 9, 'precision': 18, 'scale': 0, 'is_nullable': False, 'is_identity': True, 'is_primary_key': 0}
  - {'name': 'BKZIP_ZIP', 'data_type': 'varchar', 'max_length': 7, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_STATE', 'data_type': 'varchar', 'max_length': 2, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_CITY', 'data_type': 'varchar', 'max_length': 30, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_FIPS', 'data_type': 'varchar', 'max_length': 5, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_AREACODE', 'data_type': 'int', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_WAREHOUSE', 'data_type': 'varchar', 'max_length': 10, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_SLSP', 'data_type': 'int', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_SLSP2', 'data_type': 'int', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_TAXRATE', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_MAIL', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_LONG', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_LAT', 'data_type': 'float', 'max_length': 8, 'precision': 53, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_LOCAL', 'data_type': 'varchar', 'max_length': 1, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_ALTSILOC', 'data_type': 'varchar', 'max_length': 50, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_STOCKLOC', 'data_type': 'varchar', 'max_length': 10, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
  - {'name': 'BKZIP_ALTSTLOC', 'data_type': 'varchar', 'max_length': 50, 'precision': 0, 'scale': 0, 'is_nullable': False, 'is_identity': False, 'is_primary_key': 0}
Indexes:
  - {'name': None, 'type': 'HEAP', 'is_unique': False, 'columns': []}
Lookup Keys: ['BKZIP_ZIP']


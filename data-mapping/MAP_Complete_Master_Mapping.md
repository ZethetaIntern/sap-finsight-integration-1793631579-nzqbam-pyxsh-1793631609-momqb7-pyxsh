# Complete Enterprise Data Mapping Specification (56 Mappings across 10 Domains)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Summary of Mapped Domains
| Domain Code | Domain Name | Field Count | Primary Source SAP Tables | Target Canonical Entity |
|:---|:---|:---:|:---|:---|
| **DOM-01** | General Ledger | 12 | ACDOCA, BKPF, BSEG | `CanonicalJournalEntry` |
| **DOM-02** | Accounts Payable | 8 | BSIK, BSAK, LFA1, LFC1 | `CanonicalVendorInvoice` |
| **DOM-03** | Accounts Receivable | 8 | BSID, BSAD, KNA1, KNC1 | `CanonicalCustomerReceivable` |
| **DOM-04** | Cost Centre Accounting | 6 | CSKS, CSKT, COSP, COSS, SETNODE | `CanonicalCostCentre` |
| **DOM-05** | Profit Centre Accounting | 4 | CEPC, CEPCT | `CanonicalProfitCentre` |
| **DOM-06** | Material Ledger | 5 | MBEW, MLCD, CKMLCR | `CanonicalMaterialCost` |
| **DOM-07** | Purchase Orders | 4 | EKKO, EKPO, EKET | `CanonicalPurchaseOrder` |
| **DOM-08** | Sales Orders | 3 | VBAK, VBAP, VBEP | `CanonicalSalesOrder` |
| **DOM-09** | Fixed Assets | 3 | ANLA, ANLZ, ANLP | `CanonicalFixedAsset` |
| **DOM-10** | Bank Statements | 3 | FEBKO, FEBEP | `CanonicalBankStatement` |
| **Total** | **10 Domains** | **56** | **23 SAP Standard Tables** | **10 Target Schemas** |

---

## 2. Detailed Field-Level Mapping Catalog

### Domain 1: General Ledger (GL) - 12 Mappings
*Primary SAP Tables:* `ACDOCA` (Universal Journal), `BKPF` (Accounting Header), `BSEG` (Document Segment)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-GL-001** | GL | `ACDOCA.BUKRS` + `GJAHR` + `BELNR` + `BUZEI` | `journalEntry.documentId` | String | `CONCAT(BUKRS,'-',GJAHR,'-',LTRIM(BELNR,'0'),'-',BUZEI)` | NOT NULL; regex `^[A-Z0-9]{4}-\d{4}-\d{1,10}-\d{3}$` | Route to DLQ (`ERR-MAP-001`) | Composite unique line-item key across company codes |
| **MAP-GL-002** | GL | `ACDOCA.BUDAT` | `journalEntry.postingDate` | ISO Date | `FORMAT(BUDAT, 'YYYY-MM-DD')` from `YYYYMMDD` | NOT NULL; date <= current_date + 1 day | Route to DLQ (`ERR-MAP-002`) | Official general ledger posting date |
| **MAP-GL-003** | GL | `ACDOCA.BLDAT` | `journalEntry.documentDate` | ISO Date | `FORMAT(BLDAT, 'YYYY-MM-DD')` from `YYYYMMDD` | NOT NULL; date <= postingDate + 30 days | Default to postingDate if invalid (`ERR-MAP-002`) | Physical invoice or transaction origin date |
| **MAP-GL-004** | GL | `ACDOCA.RACCT` | `journalEntry.glAccount` | String | `LTRIM(RACCT, '0')` then lookup FinSight Chart of Accounts | Must exist in FinSight CoA master dimension | Route to Business Exception (`ERR-MAP-003`) | Chart of accounts nominal general ledger account |
| **MAP-GL-005** | GL | `ACDOCA.HSL` | `journalEntry.amountLC` | Decimal(15,2)| `DECIMAL(ABS(HSL), 2)` in company code currency (INR) | NOT NULL; range -999,999,999.99 to 999,999,999.99 | Route to DLQ (`ERR-MAP-006`) | Financial line item amount in Local Currency (INR) |
| **MAP-GL-006** | GL | `ACDOCA.WSL` | `journalEntry.amountTC` | Decimal(15,2)| `DECIMAL(ABS(WSL), 2)` in original transaction currency | NOT NULL; matches transaction currency decimals | Route to DLQ (`ERR-MAP-006`) | Transaction currency original amount |
| **MAP-GL-007** | GL | `ACDOCA.RHCUR` | `journalEntry.localCurrency` | String(3) | Direct mapping; uppercase trim | Must be valid ISO 4217 code (default `INR`) | Default to 'INR' (`ERR-MAP-004`) | Company code currency code |
| **MAP-GL-008** | GL | `ACDOCA.RWCUR` | `journalEntry.transactionCurrency` | String(3) | Direct mapping; uppercase trim | Must be valid ISO 4217 code (e.g. `USD`, `EUR`) | Default to localCurrency (`ERR-MAP-004`) | Currency in which transaction was initiated |
| **MAP-GL-009** | GL | `ACDOCA.DRCRK` | `journalEntry.postingType` | Enum | `IF DRCRK == 'S' THEN 'DEBIT' ELSE 'CREDIT'` | Must be either 'DEBIT' or 'CREDIT' | Route to DLQ (`ERR-MAP-001`) | Accounting debit/credit indicator |
| **MAP-GL-010** | GL | `ACDOCA.KOSTL` | `journalEntry.costCentre` | String | `IF KOSTL IS NULL THEN NULL ELSE LTRIM(KOSTL,'0')` | If present, must exist in Cost Centre dimension | Route to Business Exception (`ERR-MAP-003`) | Departmental overhead cost assignment |
| **MAP-GL-011** | GL | `ACDOCA.PRCTR` | `journalEntry.profitCentre` | String | `IF PRCTR IS NULL THEN NULL ELSE LTRIM(PRCTR,'0')` | If present, must exist in Profit Centre dimension | Route to Business Exception (`ERR-MAP-003`) | Business unit margin and segment assignment |
| **MAP-GL-012** | GL | `ACDOCA.MONAT` + `BKPF.BLART` | `journalEntry.fiscalPeriod` | String | `MAP_FISCAL_PERIOD(BUKRS, GJAHR, MONAT)` (e.g. 012 -> '2026-03') | Range 001-016; flag special periods 013-016 | Apply default mapping (`ERR-MAP-002`) | Fiscal accounting period mapped to calendar |

---

### Domain 2: Accounts Payable (AP) - 8 Mappings
*Primary SAP Tables:* `BSIK` (Open Items), `BSAK` (Cleared Items), `LFA1` (Vendor Master), `LFC1` (Vendor Balances)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-AP-001** | AP | `BSIK.LIFNR` | `vendorInvoice.vendorId` | String | `CONCAT('V-', LTRIM(LIFNR, '0'))` | NOT NULL; alphanumeric | Route to DLQ (`ERR-MAP-001`) | Unique enterprise vendor master number |
| **MAP-AP-002** | AP | `LFA1.NAME1` | `vendorInvoice.vendorName` | String | Trim and sanitize special characters | NOT NULL; length <= 100 | Default to 'UNKNOWN VENDOR' | Registered legal name of supplier |
| **MAP-AP-003** | AP | `BSIK.BELNR` | `vendorInvoice.invoiceNumber` | String | `LTRIM(BELNR, '0')` | NOT NULL; regex `^[0-9]{1,10}$` | Route to DLQ (`ERR-MAP-001`) | SAP AP invoice document reference |
| **MAP-AP-004** | AP | `BSIK.ZFBDT` + `BSIK.ZBD1T` | `vendorInvoice.dueDate` | ISO Date | `CALCULATE_DUE_DATE(ZFBDT, ZBD1T)` | Valid ISO date; dueDate >= baselineDate | Flag `DUE_DATE_UNCERTAIN` | Net invoice payment maturity date |
| **MAP-AP-005** | AP | `BSIK.DMBTR` | `vendorInvoice.outstandingAmountLC` | Decimal(15,2)| `DECIMAL(DMBTR, 2)` | >= 0.00 | Route to DLQ (`ERR-MAP-006`) | Outstanding payable amount in INR |
| **MAP-AP-006** | AP | `BSIK.AUGBL` | `vendorInvoice.clearingStatus` | Enum | `IF AUGBL IS NULL OR AUGBL == '' THEN 'OPEN' ELSE 'CLEARED'` | Enum: ['OPEN', 'CLEARED', 'PARTIAL'] | Default 'OPEN' | Indicator whether invoice has been paid |
| **MAP-AP-007** | AP | Current Date - `BSIK.ZFBDT` | `vendorInvoice.ageingBucket` | Enum | `COMPUTE_AGEING(ZFBDT)` -> 'CURRENT', '1-30', '31-60', '61-90', '90+' | Must match valid ageing bucket | Default 'CURRENT' | Working capital overdue stratification |
| **MAP-AP-008** | AP | `LFA1.STCD1` / `STCD2` | `vendorInvoice.taxRegistrationNumber`| String | Direct mapping; GSTIN format validation | Regex `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` | Flag `GSTIN_INVALID` | Indian GST Identification Number |

---

### Domain 3: Accounts Receivable (AR) - 8 Mappings
*Primary SAP Tables:* `BSID` (Open Customer Items), `BSAD` (Cleared), `KNA1` (Customer Master), `KNC1` (Balances)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-AR-001** | AR | `BSID.KUNNR` | `customerReceivable.customerId` | String | `CONCAT('C-', LTRIM(KUNNR, '0'))` | NOT NULL | Route to DLQ (`ERR-MAP-001`) | Unique enterprise customer account code |
| **MAP-AR-002** | AR | `KNA1.NAME1` | `customerReceivable.customerName` | String | Trim and sanitize | NOT NULL; length <= 100 | Default 'UNNAMED CUSTOMER' | Customer commercial business name |
| **MAP-AR-003** | AR | `BSID.BELNR` | `customerReceivable.invoiceNumber` | String | `LTRIM(BELNR, '0')` | NOT NULL | Route to DLQ (`ERR-MAP-001`) | SAP billing invoice reference |
| **MAP-AR-004** | AR | `BSID.DMBTR` | `customerReceivable.receivableAmountLC`| Decimal(15,2)| `DECIMAL(DMBTR, 2)` | >= 0.00 | Route to DLQ (`ERR-MAP-006`) | Outstanding receivable amount in INR |
| **MAP-AR-005** | AR | `BSID.ZFBDT` + `BSID.ZBD1T`| `customerReceivable.dueDate` | ISO Date | `CALCULATE_DUE_DATE(ZFBDT, ZBD1T)` | Valid ISO date | Default to invoiceDate + 30 | Payment due date per payment terms |
| **MAP-AR-006** | AR | `BSID.MANSP` / `MAHNS` | `customerReceivable.dunningLevel` | Integer | `INTEGER(COALESCE(MAHNS, 0))` | Range 0 to 4 | Default 0 | Dunning escalation stage (0=None, 4=Legal) |
| **MAP-AR-007** | AR | `KNA1.KLIMK` | `customerReceivable.creditLimitLC` | Decimal(15,2)| `DECIMAL(KLIMK, 2)` | >= 0.00 | Default 0.00 | Approved corporate credit ceiling |
| **MAP-AR-008** | AR | Current Date - `BSID.ZFBDT` | `customerReceivable.overdueDays` | Integer | `MAX(0, DATEDIFF(NOW(), dueDate))` | Integer >= 0 | Default 0 | Days past contractual due date |

---

### Domain 4: Cost Centre Accounting (CO-OM) - 6 Mappings
*Primary SAP Tables:* `CSKS` (Cost Centre Master), `CSKT` (Texts), `COSP` (External Postings), `SETNODE` (Hierarchies)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-CO-001** | CO | `CSKS.KOKRS` + `CSKS.KOSTL`| `costCentre.costCentreId` | String | `CONCAT(KOKRS, '-', LTRIM(KOSTL, '0'))` | NOT NULL | Route to DLQ | Controlling Area + Cost Centre composite code |
| **MAP-CO-002** | CO | `CSKT.KTEXT` | `costCentre.costCentreName` | String | Trim text (SPRAS = 'E') | NOT NULL | Default 'UNNAMED CC' | Cost Centre short description |
| **MAP-CO-003** | CO | `CSKS.VERAK` | `costCentre.costCentreOwner` | String | Trim text | Optional | Default 'UNASSIGNED' | Departmental manager responsible |
| **MAP-CO-004** | CO | `SETNODE.SETNAME` (Hierarchy) | `costCentre.hierarchyLevel1` | String | `FLATTEN_HIERARCHY(KOSTL, 1)` | NOT NULL | Default 'ROOT_NODE' | Top-tier organizational group (e.g. Manufacturing) |
| **MAP-CO-005** | CO | `SETNODE.SUBSETNAME` | `costCentre.hierarchyLevel2` | String | `FLATTEN_HIERARCHY(KOSTL, 2)` | NOT NULL | Default 'OPERATIONAL_DIV' | Sub-division (e.g. Engine Components) |
| **MAP-CO-006** | CO | `COSP.WKG001` - `WKG016` | `costCentre.actualCostTotal` | Decimal(15,2)| `SUM(WKG001..WKG016)` for period | NOT NULL | Route to DLQ | Cumulative actual expenses incurred |

---

### Domain 5: Profit Centre Accounting (CO-PCA) - 4 Mappings
*Primary SAP Tables:* `CEPC` (Profit Centre Master), `CEPCT` (Texts)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-PC-001** | PCA | `CEPC.PRCTR` | `profitCentre.profitCentreId` | String | `CONCAT('PC-', LTRIM(PRCTR, '0'))` | NOT NULL | Route to DLQ | Unique profit centre business identifier |
| **MAP-PC-002** | PCA | `CEPCT.KTEXT` | `profitCentre.profitCentreName` | String | Trim text (SPRAS = 'E') | NOT NULL | Default 'UNNAMED PC' | Business unit commercial title |
| **MAP-PC-003** | PCA | `CEPC.SEGMENT` | `profitCentre.segmentCode` | String | Trim text | NOT NULL | Default 'UNALLOCATED' | IND-AS 108 operating segment (e.g. Automotive) |
| **MAP-PC-004** | PCA | `CEPC.DATBI` | `profitCentre.validUntilDate` | ISO Date | `FORMAT(DATBI, 'YYYY-MM-DD')` | Valid date | Default '9999-12-31' | Master data organizational validity end date |

---

### Domain 6: Material Ledger (CO-PC) - 5 Mappings
*Primary SAP Tables:* `MBEW` (Material Valuation), `MLCD` (Material Ledger Documents), `CKMLCR` (Costing Records)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-ML-001** | ML | `MBEW.MATNR` + `MBEW.BWKEY` | `materialCost.materialId` | String | `CONCAT(LTRIM(MATNR, '0'), '-', BWKEY)` | NOT NULL | Route to DLQ | Material number + valuation area (Plant) |
| **MAP-ML-002** | ML | `MBEW.VPRSV` | `materialCost.priceControl` | Enum | `IF VPRSV == 'S' THEN 'STANDARD' ELSE 'MOVING_AVG'` | Enum: ['STANDARD', 'MOVING_AVG'] | Default 'STANDARD' | Inventory price valuation methodology |
| **MAP-ML-003** | ML | `MBEW.STPRS` | `materialCost.standardPriceLC` | Decimal(15,2)| `DECIMAL(STPRS / PEINH, 2)` | >= 0.00 | Route to DLQ | Standard unit inventory price in INR |
| **MAP-ML-004** | ML | `MBEW.VERPR` | `materialCost.movingAveragePriceLC`| Decimal(15,2)| `DECIMAL(VERPR / PEINH, 2)` | >= 0.00 | Route to DLQ | Weighted moving average unit price in INR |
| **MAP-ML-005** | ML | `CKMLCR.PRDIF` | `materialCost.priceDifferenceLC` | Decimal(15,2)| `DECIMAL(PRDIF, 2)` | Decimal | Default 0.00 | Purchase price / production cost variance |

---

### Domain 7: Purchase Orders (MM-PUR) - 4 Mappings
*Primary SAP Tables:* `EKKO` (PO Header), `EKPO` (PO Item), `EKET` (PO Schedule Lines)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-PO-001** | PO | `EKKO.EBELN` + `EKPO.EBELP` | `purchaseOrder.poLineItemId` | String | `CONCAT(EBELN, '-', EBELP)` | NOT NULL | Route to DLQ | Unique purchase order line item identifier |
| **MAP-PO-002** | PO | `EKKO.LIFNR` | `purchaseOrder.vendorId` | String | `CONCAT('V-', LTRIM(LIFNR, '0'))` | NOT NULL | Route to DLQ | Contracted procurement vendor code |
| **MAP-PO-003** | PO | `EKPO.NETWR` | `purchaseOrder.netOrderAmountLC`| Decimal(15,2)| `CONVERT_CURRENCY(NETWR, EKKO.WAERS, 'INR')` | >= 0.00 | Route to DLQ | Total net line item value normalized to INR |
| **MAP-PO-004** | PO | `EKPO.ELIKZ` | `purchaseOrder.isDeliveryComplete` | Boolean | `IF ELIKZ == 'X' THEN TRUE ELSE FALSE` | Boolean | Default FALSE | Goods receipt completion indicator |

---

### Domain 8: Sales Orders (SD-SLS) - 3 Mappings
*Primary SAP Tables:* `VBAK` (Sales Order Header), `VBAP` (Sales Order Item)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-SO-001** | SO | `VBAK.VBELN` + `VBAP.POSNR` | `salesOrder.orderLineItemId` | String | `CONCAT(VBELN, '-', POSNR)` | NOT NULL | Route to DLQ | Unique commercial sales order line item |
| **MAP-SO-002** | SO | `VBAK.KUNNR` | `salesOrder.customerId` | String | `CONCAT('C-', LTRIM(KUNNR, '0'))` | NOT NULL | Route to DLQ | Purchasing customer corporate identifier |
| **MAP-SO-003** | SO | `VBAP.NETWR` | `salesOrder.netAmountLC` | Decimal(15,2)| `CONVERT_CURRENCY(NETWR, VBAK.WAERK, 'INR')` | >= 0.00 | Route to DLQ | Contracted sales value converted to INR |

---

### Domain 9: Fixed Assets (FI-AA) - 3 Mappings
*Primary SAP Tables:* `ANLA` (Asset Master), `ANLZ` (Time-Dependent Data), `ANLP` (Asset Periodic Values)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-FA-001** | FA | `ANLA.BUKRS` + `ANLN1` + `ANLN2` | `fixedAsset.assetId` | String | `CONCAT(BUKRS, '-', ANLN1, '-', ANLN2)` | NOT NULL | Route to DLQ | Unique asset register item number |
| **MAP-FA-002** | FA | `ANLA.AKTIV` | `fixedAsset.capitalizationDate` | ISO Date | `FORMAT(AKTIV, 'YYYY-MM-DD')` | Valid date | Default NULL | Date asset placed in active commercial service |
| **MAP-FA-003** | FA | `ANLP.NAFAG` | `fixedAsset.accumulatedDepreciationLC` | Decimal(15,2)| `DECIMAL(NAFAG, 2)` | >= 0.00 | Route to DLQ | Cumulative straight-line / WDV depreciation |

---

### Domain 10: Bank Statements (FI-BL) - 3 Mappings
*Primary SAP Tables:* `FEBKO` (Electronic Bank Statement Header), `FEBEP` (Statement Line Items)

| Map ID | Domain | SAP Source Field | Target Field | Data Type | Transformation Logic | Validation Rule | Error Handling | Business Meaning |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **MAP-BS-001** | BS | `FEBKO.KUKEY` + `FEBEP.ESNUM` | `bankStatement.statementLineId` | String | `CONCAT(KUKEY, '-', ESNUM)` | NOT NULL | Route to DLQ | Electronic statement line item identifier |
| **MAP-BS-002** | BS | `FEBEP.VALUT` | `bankStatement.valueDate` | ISO Date | `FORMAT(VALUT, 'YYYY-MM-DD')` | Valid date | Route to DLQ | Bank clearing value date for cash positioning |
| **MAP-BS-003** | BS | `FEBEP.KWBDT` | `bankStatement.transactionAmountLC` | Decimal(15,2)| `DECIMAL(KWBDT, 2)` | Decimal | Route to DLQ | Cash deposit (positive) or disbursement (negative) |

# Enterprise Data Quality & Validation Rules Catalog (28 Rules)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Data Quality Dimension Framework
Data quality enforcement is categorized across 6 primary control categories:
1. **Null & Completeness Checks** (DQR-01 to DQR-05)
2. **Format & Data Type Validation** (DQR-06 to DQR-10)
3. **Range & Numerical Boundary Checks** (DQR-11 to DQR-15)
4. **Referential Integrity & Master Cross-Checks** (DQR-16 to DQR-20)
5. **Cross-Field Relational Validation** (DQR-21 to DQR-24)
6. **Statutory & Business Accounting Rules** (DQR-25 to DQR-28)

---

## 2. Master Data Quality Rules Catalog

| Rule ID | Category | Target Domain | Field(s) Evaluated | Validation Condition & Logic | Severity | Action on Failure |
|:---|:---|:---|:---|:---|:---:|:---|
| **DQR-01** | Null Check | GL | `documentId`, `companyCode` | Field must NOT be NULL or empty string `""` | Fatal | Reject record to DLQ (`ERR-MAP-001`) |
| **DQR-02** | Null Check | GL | `postingDate`, `glAccount` | Field must NOT be NULL or whitespace | Fatal | Reject record to DLQ (`ERR-MAP-001`) |
| **DQR-03** | Null Check | GL | `amountLC`, `localCurrency` | Field must NOT be NULL; currency must exist | Fatal | Reject record to DLQ (`ERR-MAP-001`) |
| **DQR-04** | Null Check | AP | `vendorId`, `invoiceNumber` | Field must NOT be NULL | Fatal | Reject record to DLQ (`ERR-MAP-001`) |
| **DQR-05** | Null Check | AR | `customerId`, `receivableAmountLC`| Field must NOT be NULL | Fatal | Reject record to DLQ (`ERR-MAP-001`) |
| **DQR-06** | Format | Cross | Dates (`postingDate`, `dueDate`)| Must conform to ISO 8601 regex `^\d{4}-\d{2}-\d{2}$` | Error | Sanitize format; else DLQ (`ERR-MAP-002`) |
| **DQR-07** | Format | Cross | Currency (`localCurrency`) | Must be valid 3-letter ISO 4217 uppercase code | Error | Lookup mapping table; else DLQ (`ERR-MAP-004`) |
| **DQR-08** | Format | AP/AR | GSTIN (`taxRegistrationNumber`)| Regex `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` | Warning | Tag record `FLAG_GSTIN_INVALID`; pass through |
| **DQR-09** | Format | GL | `documentId` Composite Key | Regex `^[A-Z0-9]{4}-\d{4}-\d{1,10}-\d{3}$` | Fatal | Reject record to DLQ (`ERR-MAP-001`) |
| **DQR-10** | Format | GL/CO | `glAccount`, `costCentre` | Must be numeric string after leading zero trim | Error | Strip non-numeric chars; else DLQ |
| **DQR-11** | Range | GL | `amountLC`, `amountTC` | Value must be between -999,999,999.99 and 999,999,999.99 | Fatal | Reject record to DLQ (`ERR-MAP-006`) |
| **DQR-12** | Range | GL | `fiscalPeriod` | Fiscal period string must be in range `YYYY-01` to `YYYY-12` | Error | Apply period default (`ERR-MAP-002`) |
| **DQR-13** | Range | AR | `dunningLevel` | Must be integer between 0 and 4 | Error | Clamp to range 0..4; flag warning |
| **DQR-14** | Range | GL/AP | `postingDate` Boundary | Date must NOT be in future (`<= current_date + 1 day`) | Fatal | Reject record to DLQ (`ERR-VAL-007`) |
| **DQR-15** | Range | GL/AP | `documentDate` Historical Cap | Date must NOT be older than 5 years | Warning | Tag record `HISTORICAL_AUDIT_ADJ` |
| **DQR-16** | Ref Integrity| GL/CO | `costCentre` Dimension | If present, cost centre must exist in cached active CC master | Error | Route to Business Exception Queue (`ERR-MAP-003`) |
| **DQR-17** | Ref Integrity| GL/PCA | `profitCentre` Dimension | If present, profit centre must exist in active PC master | Error | Route to Business Exception Queue (`ERR-MAP-003`) |
| **DQR-18** | Ref Integrity| GL | `glAccount` Chart of Accounts | Account code must exist in FinSight Chart of Accounts | Fatal | Reject record to DLQ (`ERR-MAP-003`) |
| **DQR-19** | Ref Integrity| AP | `vendorId` Master Data | Vendor must exist in active Vendor Master list | Warning | Tag record `NEW_VENDOR_PENDING_SYNC` |
| **DQR-20** | Ref Integrity| AR | `customerId` Master Data | Customer must exist in active Customer Master list | Warning | Tag record `NEW_CUSTOMER_PENDING_SYNC` |
| **DQR-21** | Cross-Field | GL | `documentDate` vs `postingDate` | `documentDate` must be `<= postingDate + 30 days` | Error | Overwrite `documentDate = postingDate` |
| **DQR-22** | Cross-Field | GL | `postingType` vs `amountLC` | If `postingType == 'CREDIT'`, line balance matches credit sign | Error | Enforce sign consistency |
| **DQR-23** | Cross-Field | AP | `dueDate` vs Baseline Date | `dueDate` must be `>= baselineDate (ZFBDT)` | Error | Recalculate `dueDate = ZFBDT + ZBD1T` |
| **DQR-24** | Cross-Field | ML | Standard vs Moving Average | If `priceControl == 'S'`, `standardPriceLC` must be > 0.00 | Error | Fallback to moving average price; flag warning |
| **DQR-25** | Business | GL | Batch Balance Zero-Sum | `SUM(Debits) - SUM(Credits) == 0.00` across balanced journal | Fatal | Halt batch commitment; trigger alert |
| **DQR-26** | Business | GL | Multi-Company Separation | Company Code in payload must strictly match tenant authorization | Fatal | Reject unauthorized company code (`ERR-LOAD-006`) |
| **DQR-27** | Business | AP/AR | Duplicate Invoice Prevention | Same `vendorId` + `invoiceNumber` within 365 days rejected | Fatal | Reject duplicate (`ERR-LOAD-004`) |
| **DQR-28** | Business | GL | Special Period Postings | Special periods 013-016 allowed only for audit/closing document types | Warning | Tag record `SPECIAL_AUDIT_POSTING` |

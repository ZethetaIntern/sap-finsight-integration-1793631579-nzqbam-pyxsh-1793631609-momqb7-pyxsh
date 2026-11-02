# Advanced Transformation Rules: Fiscal-to-Calendar Period Mapping
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document ID:** TR-FISC-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Business Context
Meridian Manufacturing follows the standard Indian Fiscal Year calendar running from **April 1 to March 31**. In SAP S/4HANA, Company Codes `MC01`, `MC02`, and `MC03` utilize Fiscal Year Variant `V3` (April to March, 12 normal periods + 4 special audit adjustment periods).

In contrast, Zetheta FinSight 4.2 standardizes financial analytics on Gregorian calendar months and quarters to align with international benchmarking.

---

## 2. Period Mapping Logic Table

| SAP Fiscal Period (`MONAT`) | Calendar Month | Gregorian Quarter | Indian Fiscal Quarter | Special Audit Period Flag | FinSight Target Period String |
|:---:|:---:|:---:|:---:|:---:|:---:|
| `001` | April | Q2 | Q1 | `false` | `YYYY-04` |
| `002` | May | Q2 | Q1 | `false` | `YYYY-05` |
| `003` | June | Q2 | Q1 | `false` | `YYYY-06` |
| `004` | July | Q3 | Q2 | `false` | `YYYY-07` |
| `005` | August | Q3 | Q2 | `false` | `YYYY-08` |
| `006` | September | Q3 | Q2 | `false` | `YYYY-09` |
| `007` | October | Q4 | Q3 | `false` | `YYYY-10` |
| `008` | November | Q4 | Q3 | `false` | `YYYY-11` |
| `009` | December | Q4 | Q3 | `false` | `YYYY-12` |
| `010` | January | Q1 | Q4 | `false` | `(YYYY+1)-01` |
| `011` | February | Q1 | Q4 | `false` | `(YYYY+1)-02` |
| `012` | March | Q1 | Q4 | `false` | `(YYYY+1)-03` |
| `013` | March (Audit Postings) | Q1 | Q4 | `true` | `(YYYY+1)-03` |
| `014` | March (Tax Provisions)| Q1 | Q4 | `true` | `(YYYY+1)-03` |
| `015` | March (Statutory Adj)  | Q1 | Q4 | `true` | `(YYYY+1)-03` |
| `016` | March (Final Close)    | Q1 | Q4 | `true` | `(YYYY+1)-03` |

### 2.1 Transformation Algorithm
```typescript
export function mapFiscalPeriod(gjahr: number, monat: string): { period: string; isSpecial: boolean } {
  const periodNum = parseInt(monat, 10);
  if (periodNum >= 1 && periodNum <= 9) {
    const monthStr = String(periodNum + 3).padStart(2, '0');
    return { period: `${gjahr}-${monthStr}`, isSpecial: false };
  } else if (periodNum >= 10 && periodNum <= 12) {
    const monthStr = String(periodNum - 9).padStart(2, '0');
    return { period: `${gjahr + 1}-${monthStr}`, isSpecial: false };
  } else if (periodNum >= 13 && periodNum <= 16) {
    // Audit adjustment periods mapped to March of fiscal closing year
    return { period: `${gjahr + 1}-03`, isSpecial: true };
  } else {
    throw new Error(`ERR-MAP-002: Invalid fiscal period ${monat}`);
  }
}
```

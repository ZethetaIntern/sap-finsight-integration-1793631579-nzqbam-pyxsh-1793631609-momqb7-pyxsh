# Advanced Transformation Rules: Currency Conversion Specification
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document ID:** TR-CURR-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Objective & Governing Standards
Meridian Manufacturing Ltd. transacts in multi-currency environments (automotive exports in USD/EUR, Japanese precision tooling imports in JPY), but consolidates all FinSight financial reporting in **Corporate Group Currency: Indian Rupee (INR)**.

Currency conversions must strictly adhere to **IND-AS 21 / IAS 21 (The Effects of Changes in Foreign Exchange Rates)**.

---

## 2. SAP Exchange Rate Feeds (`TCURR`)
The integration service caches daily exchange rates from SAP table `TCURR` using exchange rate type `M` (Standard translation at average rate).

```
SAP Table TCURR Structure:
- KURST : Exchange Rate Type ('M')
- FCURR : From Currency (e.g. 'USD')
- TCURR : To Currency (e.g. 'INR')
- GDATU : Inverted Date Formula: GDATU = 99999999 - YYYYMMDD
- UKURS : Direct Exchange Rate (or indirect if negative)
- FFACT : From Ratio Factor (e.g. 1)
- TFACT : To Ratio Factor (e.g. 1 or 100 for JPY)
```

### 2.1 Conversion Mathematical Algorithm
```
Effective Rate (R) = (UKURS * (TFACT / FFACT))
Converted Amount (INR) = ROUND(Original Amount * R, 2)
```

### 2.2 Missing Rate & Weekend Fallback Policy
1. If no exact match exists for transaction date `T`, the engine searches backwards up to 4 calendar days (`T-1`, `T-2`, `T-3`, `T-4`) to capture Friday rates for weekend transactions.
2. If rate is found within 4 days, conversion proceeds, but the transformed payload sets audit flag:
   `"isStaleRate": true, "rateDateUsed": "2026-03-13"`
3. If no rate is found within 4 days, conversion halts with error code **`ERR-MAP-005`** and routes the record to the Dead Letter Queue.

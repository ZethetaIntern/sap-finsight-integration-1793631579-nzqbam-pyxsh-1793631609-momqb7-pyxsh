# Rollback Procedure & Contingency Decision Matrix
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** DEP-ROLLBACK-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Rollback Decision Governance Matrix
The decision to abort deployment and initiate rollback is governed strictly by the following matrix:

| Trigger Condition | Severity | Max Assessment Time | Decision Authority | Rollback Action |
|:---|:---:|:---:|:---|:---|
| SAP CDS View transport failure / syntax dump | Critical | 15 minutes | Priya Deshmukh | Rollback SAP transports via CTS+ (`DEVK900142_UNDO`) |
| Network bandwidth exceeds 25% cap under load | High | 15 minutes | Rajesh Venkataraman | Clamp rate limiters; if unresolvable, abort deployment |
| FinSight Ingestion API unreachable (> 30 mins) | Critical | 20 minutes | Marcus Wei | Halt container deployment; revert DNS routes |
| Reconciliation debit/credit break > 0.00 INR | Critical | 20 minutes | Ananya Krishnan | Purge smoke batch in FinSight; preserve SAP state |
| Total deployment time reaches 01:30 IST (T+3.5h)| High | Immediate | Incident Commander | Execute full orchestrated rollback procedure |

---

## 2. Chronological Rollback Execution Steps
1. **Halt Schedulers & Workers (T+0m):** Scale Kubernetes deployments to 0 replicas:  
   `kubectl scale deployment --all --replicas=0 -n meridian-integration`
2. **Purge Staging Ingestion in FinSight (T+5m):** Execute tenant batch rollback API:  
   `POST /api/v1/tenant/MERIDIAN-PROD/rollback-batch?batchId=SMOKE-TEST`
3. **Reset SAP ODP Delta Pointers (T+15m):** In SAP transaction `ODQ_MON`, re-point subscription delta cursor to pre-deployment timestamp.
4. **Revert Database Schema Migrations (T+25m):** Execute rollback migration:  
   `npm run db:migrate:undo`
5. **Re-enable Legacy Batch Dumps (T+35m):** Un-pause legacy end-of-day ABAP CSV export batch jobs.
6. **Post-Mortem Declaration (T+45m):** Issue notification to executive stakeholders declaring successful rollback to pre-maintenance baseline; schedule post-mortem review.

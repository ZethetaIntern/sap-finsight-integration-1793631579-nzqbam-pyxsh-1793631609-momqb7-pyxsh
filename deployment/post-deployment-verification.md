# Post-Deployment Verification Protocol (12 Checks)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** DEP-VERIF-01  
**Classification:** Strictly Private & Confidential  

---

| Check ID | Verification Area | Validation Command / Verification Action | Expected Outcome | Pass/Fail |
|:---:|:---|:---|:---|:---:|
| **VER-01** | Extractor Pod Health | `kubectl get pods -l app=sap-extractor` | Status: `Running`, Restarts: 0 | PASS |
| **VER-02** | Transformer Pod Health | `kubectl get pods -l app=transform-worker` | Status: `Running`, Restarts: 0 | PASS |
| **VER-03** | FinSight Loader Health | `kubectl get pods -l app=finsight-loader` | Status: `Running`, Restarts: 0 | PASS |
| **VER-04** | SAP RFC Gateway Ping | Run `RFC_PING` via connection pool manager | Latency < 25ms over MPLS | PASS |
| **VER-05** | ODP Delta Subscription | Check SAP `RSA1` / `ODQ_MON` delta queue monitor | Subscriptions ACTIVE for all 12 domains | PASS |
| **VER-06** | OAuth Token Generation | `curl -X POST https://auth.finsight.zetheta.com/oauth/v2/token` | 200 OK, valid RS256 JWT, TTL 3600s | PASS |
| **VER-07** | Ingestion Canary Call | Dispatch synthetic journal entry with test flag | 201 Created from FinSight Ingress | PASS |
| **VER-08** | Idempotency Verification| Re-dispatch identical synthetic journal entry | 200 OK (Skipped duplicate, no second write) | PASS |
| **VER-09** | DLQ Pipeline Routing | Inject 1 malformed record into test stream | Trapped in DLQ topic and DB store | PASS |
| **VER-10** | Recon Zero Break | Execute batch reconciliation on smoke batch | Delta Debit/Credit Variance == 0.00 INR | PASS |
| **VER-11** | Prometheus Scraping | Inspect Prometheus target list (`/targets`) | All 8 integration targets `UP` | PASS |
| **VER-12** | Grafana Dashboard | Inspect 12-panel dashboard in Grafana | All panels rendering live data; MON-001 GREEN | PASS |

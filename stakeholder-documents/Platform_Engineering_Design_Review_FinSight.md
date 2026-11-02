# Platform Engineering Design Review (3-5 Pages)
**Target Audience:** Marcus Wei, Principal Platform Engineer, Zetheta FinSight 4.2  
**Author:** Forward Deployed Engineering (FDE) Team  
**Date:** November 2026 | **Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## Section 1: Ingestion API Contracts & Interaction Model
*[Assumed Contract: Standard Zetheta FinSight 4.2 REST Specification]*

The integration service dispatches canonical, validated accounting events to FinSight ingestion microservices via HTTP/2 over TLS 1.3:
- **Batch Size:** Fixed micro-batches of **500 records per POST request** (Payload size: ~185 KB gzipped).
- **HTTP Headers:**
  - `Content-Type: application/json`
  - `Content-Encoding: gzip`
  - `Authorization: Bearer <JWT_TOKEN>`
  - `X-Tenant-ID: MERIDIAN-PROD`
  - `X-Idempotency-Key: <UUIDv4>`
  - `X-Correlation-ID: <UUIDv4>`

### 1.1 Sample cURL Request
```bash
curl -X POST "https://api-mumbai.finsight.zetheta.com/v1/financial/journal-entries/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1Ni..." \
  -H "X-Tenant-ID: MERIDIAN-PROD" \
  -H "X-Idempotency-Key: c9b8a120-1284-48a5-b1e2-9f37a5482310" \
  -d @microbatch_gl_500.json
```

---

## Section 2: OAuth 2.0 Authentication & Token Lifecycle
```
Integration Loader                  Azure AD / FinSight OAuth                FinSight Ingestion API
       |                                       |                                       |
       |--- 1. POST /oauth/v2/token ---------->|                                       |
       |    (client_credentials grant)         |                                       |
       |<-- 2. 200 OK (access_token, 3600s) ---|                                       |
       |                                                                               |
       |=== 3. Ingestion Loop (T=0 to T=3480s) =======================================>|
       |    POST /v1/financial/journal-entries/batch (Bearer Token)                    |
       |                                                                               |
       |--- 4. Preemptive Refresh at T-120s -->|                                       |
       |<-- 5. 200 OK (new access_token) ------|                                       |
       |                                                                               |
       |=== 6. Seamless Continuation (Zero 401 Interruptions) ========================>|
```

---

## Section 3: Ingestion Throughput Expectations & Platform Limits

| Metric Attribute | Average Regular Baseline | Peak Month-End Volume | Technical Limit / Ceiling |
|:---|:---:|:---:|:---:|
| **Records Extracted Daily** | ~70,000 records/day | 500,000 records/batch | 1,000,000 records/day |
| **Ingestion Micro-batch Rate** | 2.5 requests/minute | 15.0 requests/minute | 30.0 requests/minute (Capped) |
| **FinSight Rate Limit Headroom** | 97.5% Quota Remaining | 85.0% Quota Remaining | Max 1,000 req/min tenant limit |
| **Target P95 Latency** | 1.38 seconds | 2.64 seconds | < 5.0 seconds SLA |

---

## Section 4: Platform Constraints Encountered & Proposed Engineering Enhancements
1. **Bulk Ingestion Endpoint for 500k Batches:**  
   *Current Observation:* Submitting 500,000 entries requires 1,000 individual micro-batch HTTP requests.  
   *Proposed Enhancement:* We request Marcus Wei's team introduce an asynchronous bulk streaming endpoint (`POST /v1/financial/bulk-stream`) accepting S3/Parquet multipart manifests for month-end batches.
2. **Dynamic Quota Header Emission:**  
   *Current Observation:* Rate-limit headroom is currently estimated client-side.  
   *Proposed Enhancement:* Request FinSight gateway return standard headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` on every response.

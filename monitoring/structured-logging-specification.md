# Enterprise Structured Logging Specification (JSON Standard)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** MON-LOG-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Mandatory 12 JSON Fields Schema
Every log entry emitted by any integration microservice must be formatted as a single-line JSON string containing exactly the following 12 mandatory top-level fields:

| Field Index | Field Name | Data Type | Mandatory | Example Value | Description & Purpose |
|:---:|:---|:---|:---:|:---|:---|
| 1 | `timestamp` | ISO 8601 String | YES | `"2026-03-15T09:31:12.450+05:30"` | UTC or IST precise event emission timestamp |
| 2 | `logLevel` | Enum | YES | `"INFO"` | Severity: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` |
| 3 | `serviceName` | String | YES | `"finsight-loader-service"` | Originating microservice component name |
| 4 | `environment` | Enum | YES | `"production"` | Operating environment: `dev`, `qa`, `staging`, `production` |
| 5 | `correlationId` | UUIDv4 String | YES | `"f47ac10b-58cc-4372-a567-0e02b2c3d479"` | End-to-end distributed trace identifier across all hops |
| 6 | `domain` | Enum | YES | `"GENERAL_LEDGER"` | Business accounting domain being processed |
| 7 | `batchId` | String | YES | `"BATCH-GL-20260315-0930"` | Deterministic extraction batch identifier |
| 8 | `documentId` | String | YES | `"MC01-2026-0100004521-001"` | Source ERP business key (or `"N/A"` for batch-level logs) |
| 9 | `plantCode` | String | YES | `"PL01"` | Originating manufacturing plant (`PL01` to `PL07` or `"ALL"`) |
| 10 | `errorCode` | String | YES | `"NONE"` / `"ERR-LOAD-001"` | Official registry error code (or `"NONE"` for success logs) |
| 11 | `durationMs` | Integer | YES | `142` | Execution latency of the logged operation in milliseconds |
| 12 | `message` | String | YES | `"Micro-batch 500 records successfully ingested into FinSight"` | Human-readable diagnostic description |

### 1.1 Sample Production Log Event (JSON)
```json
{
  "timestamp": "2026-03-15T09:31:12.450+05:30",
  "logLevel": "INFO",
  "serviceName": "finsight-loader-service",
  "environment": "production",
  "correlationId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "domain": "GENERAL_LEDGER",
  "batchId": "BATCH-GL-20260315-0930",
  "documentId": "MC01-2026-0100004521-001",
  "plantCode": "PL01",
  "errorCode": "NONE",
  "durationMs": 142,
  "message": "Micro-batch 500 records successfully ingested into FinSight"
}
```

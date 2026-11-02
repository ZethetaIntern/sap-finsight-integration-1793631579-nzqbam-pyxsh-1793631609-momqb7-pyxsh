# Resilience Strategy: Exponential Backoff, Jitter and Retry Limits
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** RES-RETRY-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Retry Eligibility Principle
To prevent the "Thundering Herd Problem" and downstream denial-of-service, retries are strictly restricted to **TRANSIENT** errors (`ERR-EXT-001`, `ERR-EXT-002`, `ERR-LOAD-001`, `ERR-LOAD-002`). Permanent errors (`ERR-LOAD-003`, `ERR-LOAD-007`) and Data Quality errors (`ERR-MAP-*`) are **NEVER** automatically retried.

---

## 2. Mathematical Backoff Formulation
The integration engine implements **Full Jitter Exponential Backoff** following AWS Architecture Best Practices:

```
Formula:
  Max_Wait = min(Cap, Base * (2 ^ Attempt))
  Actual_Wait = random_uniform(0, Max_Wait)

Parameters:
  Base = 2.0 seconds
  Cap = 60.0 seconds
  Max Retries = 3 attempts
```

### 2.1 Backoff Progression Table
| Attempt | Calculated Max Wait (`2^Attempt * 2s`) | Applied Cap | Jittered Wait Range |
|:---:|:---:|:---:|:---:|
| **1** | 4.0 seconds | 60.0 seconds | 0.00s to 4.00s |
| **2** | 8.0 seconds | 60.0 seconds | 0.00s to 8.00s |
| **3** | 16.0 seconds | 60.0 seconds | 0.00s to 16.00s |
| **Exceeded**| N/A | N/A | Diverted to Dead Letter Queue (DLQ) |

### 2.2 Rate Limit Header Precedence (`Retry-After`)
When FinSight returns HTTP 429 (`ERR-LOAD-001`) with a `Retry-After: <seconds>` response header, the loader **strictly honors the header value** plus a randomized jitter factor:
```
Wait_Duration = Retry_After_Seconds + random_uniform(0.5, 3.0)
```

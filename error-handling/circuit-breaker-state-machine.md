# Resilience Strategy: Circuit Breaker State Machine
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document Ref:** RES-CB-01  
**Classification:** Strictly Private & Confidential  

---

## 1. State Machine Blueprint

```
       +---------------------------------------------+
       |                                             |
       |               [ CLOSED ]                    |
       |       (Normal Traffic Execution)            |
       |                                             |
       +----------------------+----------------------+
                              |
     Failure Threshold        | Consecutive Successes
     (5 consecutive 5xx/time) | (3 successful probes)
                              v
       +----------------------+----------------------+
       |                                             |
       |                 [ OPEN ]                    |
       |         (Fast-Fail Mode, 60s)               |
       |                                             |
       +----------------------+----------------------+
                              |
               Reset Timeout  | Probe Request
               Expires (60s)  | Fails (1 failure)
                              v
       +---------------------------------------------+
       |                                             |
       |              [ HALF-OPEN ]                  |
       |          (Canary Probe Mode)                |
       |                                             |
       +---------------------------------------------+
```

---

## 2. Operational Parameter Configuration

| Parameter Name | Production Setting | Rationale |
|:---|:---:|:---|
| **Sliding Window Duration** | 30 seconds | Evaluates error rates across a rolling short window |
| **Failure Threshold** | 5 consecutive failures | Trips circuit breaker if downstream is genuinely down |
| **Open State Timeout** | 60 seconds | Gives FinSight backend time to recover or auto-scale |
| **Half-Open Probes Allowed**| 1 canary request | Limits exposure during recovery probing |
| **Success Threshold to Close**| 3 consecutive successes | Confirms complete downstream recovery before full flood |

### 2.1 Action During Open State
When the circuit is `OPEN`:
1. Ingestion requests fast-fail immediately without attempting network transmission.
2. Kafka consumer group pauses consumption on topic partitions to buffer incoming events.
3. Prometheus increments metric `circuit_breaker_state{service="finsight-loader"} = 1`.
4. PagerDuty P2 operational alert is dispatched to Marcus Wei and the FDE on-call engineer.

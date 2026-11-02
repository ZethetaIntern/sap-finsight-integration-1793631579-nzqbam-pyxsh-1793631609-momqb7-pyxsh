# ADR-005: Circuit Breaker Pattern for Downstream Fault Isolation
## Context
If FinSight 4.2 experiences maintenance outages, database degradation, or network timeouts, continuing to flood the target endpoint will trigger cascading failures, exhaust connection pools, and violate rate limits.

## Decision
Implement the **Martin Fowler Circuit Breaker Pattern** in the FinSight Ingestion microservice:
- **States:** `CLOSED` (Normal operations), `OPEN` (Fast-fail mode), `HALF-OPEN` (Canary probing mode).
- **Failure Threshold:** 5 consecutive HTTP 5xx or timeout errors within a 30-second sliding window.
- **Open State Duration:** 60 seconds (no outbound traffic sent; incoming Kafka consumption paused or buffered).
- **Half-Open Probe:** Dispatches a single canary request; if successful, resets to `CLOSED`; if failed, resets to `OPEN` for 120 seconds.

## Consequences
- **Positive:** Protects downstream analytics platform from denial-of-service; prevents integration worker crash loops; triggers immediate PagerDuty P2 operational alerts.
- **Negative:** Requires distributed state synchronization (via Redis or internal cluster state) if running multiple loader instances.
- **Status:** APPROVED by Marcus Wei & Rajesh Venkataraman.

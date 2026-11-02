# ADR-003: OAuth 2.0 Client Credentials Grant with Automated Pre-Expiry Refresh
## Context
FinSight 4.2 requires secure REST authentication via OAuth 2.0. Ingestion tokens expire every 3,600 seconds (1 hour). If a token expires during a 500,000-entry batch upload, in-flight requests will fail with HTTP 401 Unauthorized, risking pipeline stalls and duplicate re-transmissions.

## Decision
Implement an automated **OAuth 2.0 Token Lifecycle Manager** within the FinSight Loader microservice:
1. Authenticates against Azure AD / FinSight OAuth endpoint using `client_credentials` grant with dedicated scopes (`finsight:gl:write`, `finsight:ap:write`, etc.).
2. Tracks token TTL and triggers preemptive background refresh **120 seconds before expiry**.
3. Employs mutex locking during refresh to prevent multiple concurrent worker threads from issuing duplicate token requests.

## Consequences
- **Positive:** Zero HTTP 401 pipeline interruptions during continuous operations; thread-safe token sharing; strict adherence to least-privilege scope models.
- **Negative:** Requires secure secret storage in AWS Secrets Manager with automatic credential rotation.
- **Status:** APPROVED by Marcus Wei & Rajesh Venkataraman.

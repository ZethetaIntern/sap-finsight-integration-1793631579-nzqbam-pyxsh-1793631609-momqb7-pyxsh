import os
import json
import yaml

def generate_monitoring():
    os.makedirs(r'monitoring/grafana', exist_ok=True)
    os.makedirs(r'monitoring/prometheus', exist_ok=True)
    os.makedirs(r'monitoring/alerts', exist_ok=True)

    # 1. Grafana Dashboard JSON for all 12 Panels (MON-001 to MON-012)
    grafana_dashboard = {
        "annotations": {"list": []},
        "editable": True,
        "fiscalYearStartMonth": 4,
        "graphTooltip": 1,
        "id": None,
        "links": [],
        "liveNow": True,
        "panels": [
            {
                "id": 1,
                "title": "MON-001: Pipeline Health Overview",
                "type": "stat",
                "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                "targets": [{"expr": "sum(pipeline_health_status)", "legendFormat": "Pipeline Health"}],
                "fieldConfig": {
                    "defaults": {
                        "mappings": [
                            {"type": "value", "options": {"0": {"text": "GREEN (Healthy)", "color": "green"}}},
                            {"type": "value", "options": {"1": {"text": "YELLOW (Lag > 2h)", "color": "yellow"}}},
                            {"type": "value", "options": {"2": {"text": "RED (Breached / Down)", "color": "red"}}}
                        ]
                    }
                }
            },
            {
                "id": 2,
                "title": "MON-002: Throughput (Records/Sec)",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
                "targets": [{"expr": "sum by (domain) (rate(records_processed_total[5m]))", "legendFormat": "{{domain}}"}]
            },
            {
                "id": 3,
                "title": "MON-003: Latency Distribution (P95)",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                "targets": [{"expr": "histogram_quantile(0.95, sum(rate(api_duration_seconds_bucket[5m])) by (le))", "legendFormat": "P95 Latency (s)"}]
            },
            {
                "id": 4,
                "title": "MON-004: Error Rate (%)",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
                "targets": [{"expr": "sum(rate(errors_total[5m])) / sum(rate(requests_total[5m])) * 100", "legendFormat": "Error Rate %"}]
            },
            {
                "id": 5,
                "title": "MON-005: DLQ Depth & Lag Trend",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 0, "y": 4},
                "targets": [{"expr": "kafka_consumergroup_lag{topic=~'.*dlq.*'}", "legendFormat": "DLQ Depth"}]
            },
            {
                "id": 6,
                "title": "MON-006: Reconciliation Status",
                "type": "table",
                "gridPos": {"h": 4, "w": 6, "x": 6, "y": 4},
                "targets": [{"expr": "reconciliation_batch_status", "legendFormat": "{{domain}}"}]
            },
            {
                "id": 7,
                "title": "MON-007: SAP RFC Pool Utilisation",
                "type": "gauge",
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 4},
                "targets": [{"expr": "(sap_rfc_active_connections / 50) * 100", "legendFormat": "RFC Pool %"}]
            },
            {
                "id": 8,
                "title": "MON-008: FinSight Ingestion API Health & Rate Limits",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 4},
                "targets": [{"expr": "finsight_rate_limit_remaining", "legendFormat": "Remaining Quota"}]
            },
            {
                "id": 9,
                "title": "MON-009: Data Freshness Lag (Hours)",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8},
                "targets": [{"expr": "(time() - max by (domain) (last_successful_load_timestamp)) / 3600", "legendFormat": "{{domain}} Freshness (h)"}]
            },
            {
                "id": 10,
                "title": "MON-010: Compute Resource Utilisation (CPU/Mem)",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8},
                "targets": [
                    {"expr": "sum(container_cpu_usage_seconds_total)", "legendFormat": "CPU"},
                    {"expr": "sum(container_memory_working_set_bytes)", "legendFormat": "Memory"}
                ]
            },
            {
                "id": 11,
                "title": "MON-011: Kafka Consumer Lag by Partition",
                "type": "timeseries",
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
                "targets": [{"expr": "sum by (topic) (kafka_consumergroup_lag)", "legendFormat": "{{topic}}"}]
            },
            {
                "id": 12,
                "title": "MON-012: Circuit Breaker State",
                "type": "stat",
                "gridPos": {"h": 4, "w": 6, "x": 18, "y": 8},
                "targets": [{"expr": "circuit_breaker_state", "legendFormat": "Circuit Breaker"}],
                "fieldConfig": {
                    "defaults": {
                        "mappings": [
                            {"type": "value", "options": {"0": {"text": "CLOSED (Normal)", "color": "green"}}},
                            {"type": "value", "options": {"1": {"text": "OPEN (Tripped)", "color": "red"}}},
                            {"type": "value", "options": {"2": {"text": "HALF-OPEN (Probing)", "color": "yellow"}}}
                        ]
                    }
                }
            }
        ],
        "schemaVersion": 38,
        "title": "Meridian SAP S/4HANA to FinSight 4.2 Integration Cockpit",
        "uid": "meridian-sap-finsight-v2"
    }

    with open(r'monitoring/grafana/finsight-integration-overview.json', 'w', encoding='utf-8') as f:
        json.dump(grafana_dashboard, f, indent=2)

    # 2. Prometheus Alerting Rules (16 Rules)
    alerts = {
        "groups": [
            {
                "name": "meridian_integration_alerts",
                "rules": [
                    {
                        "alert": "DataFreshnessSlaBreach",
                        "expr": "(time() - max by (domain) (last_successful_load_timestamp)) > 14400",
                        "for": "5m",
                        "labels": {"severity": "P1", "team": "enterprise-support"},
                        "annotations": {
                            "summary": "Data freshness exceeded 4-hour SLA target for domain {{ $labels.domain }}",
                            "action": "Trigger PagerDuty P1; check extractor scheduler and Kafka queue lag.",
                            "owner": "FDE Integration Lead"
                        }
                    },
                    {
                        "alert": "ReconciliationBreakDetected",
                        "expr": "reconciliation_balance_variance_inr > 0.00",
                        "for": "0m",
                        "labels": {"severity": "P1", "team": "financial-audit"},
                        "annotations": {
                            "summary": "Debit-Credit reconciliation variance detected: {{ $value }} INR",
                            "action": "Halt downstream report publish; alert Dr. Sanjay Kulkarni & Ananya Krishnan.",
                            "owner": "Dr. Sanjay Kulkarni"
                        }
                    },
                    {
                        "alert": "SapRfcPoolExhaustionWarning",
                        "expr": "sap_rfc_active_connections > 35",
                        "for": "2m",
                        "labels": {"severity": "P2", "team": "sap-basis"},
                        "annotations": {
                            "summary": "SAP RFC connection pool utilization > 70% (35 of 50 in use)",
                            "action": "Throttle background batch extractors to protect SAP dialog users.",
                            "owner": "Priya Deshmukh"
                        }
                    },
                    {
                        "alert": "FinSightRateLimitImminent",
                        "expr": "finsight_rate_limit_remaining < 100",
                        "for": "1m",
                        "labels": {"severity": "P2", "team": "api-engineering"},
                        "annotations": {
                            "summary": "FinSight API rate limit headroom under 10%",
                            "action": "Activate client-side throttle to delay micro-batch dispatches.",
                            "owner": "Marcus Wei"
                        }
                    },
                    {
                        "alert": "CircuitBreakerOpen",
                        "expr": "circuit_breaker_state == 1",
                        "for": "30s",
                        "labels": {"severity": "P2", "team": "fde-operations"},
                        "annotations": {
                            "summary": "Circuit breaker TRIPPED to OPEN state for FinSight loader",
                            "action": "Check FinSight platform status; verify network egress connectivity.",
                            "owner": "Marcus Wei / FDE Lead"
                        }
                    },
                    {
                        "alert": "HighErrorRate",
                        "expr": "sum(rate(errors_total[5m])) / sum(rate(requests_total[5m])) * 100 > 5",
                        "for": "3m",
                        "labels": {"severity": "P1", "team": "api-engineering"},
                        "annotations": {
                            "summary": "Integration pipeline error rate exceeded 5%",
                            "action": "Inspect error code distribution; check for schema incompatibility.",
                            "owner": "FDE Developer"
                        }
                    },
                    {
                        "alert": "DlqDepthSpike",
                        "expr": "kafka_consumergroup_lag{topic=~'.*dlq.*'} > 50",
                        "for": "5m",
                        "labels": {"severity": "P2", "team": "data-governance"},
                        "annotations": {
                            "summary": "Dead Letter Queue depth exceeded 50 failed messages",
                            "action": "Alert data stewards to review Exception Portal.",
                            "owner": "Data Steward"
                        }
                    },
                    {
                        "alert": "KafkaConsumerLagCritical",
                        "expr": "sum by (topic) (kafka_consumergroup_lag) > 50000",
                        "for": "5m",
                        "labels": {"severity": "P2", "team": "platform-ops"},
                        "annotations": {
                            "summary": "Kafka consumer lag exceeded 50,000 records on {{ $labels.topic }}",
                            "action": "Scale consumer pod replicas horizontally.",
                            "owner": "Rajesh Venkataraman"
                        }
                    },
                    {
                        "alert": "OAuthTokenRefreshFailure",
                        "expr": "oauth_token_refresh_failures_total > 0",
                        "for": "0m",
                        "labels": {"severity": "P1", "team": "security-ops"},
                        "annotations": {
                            "summary": "Preemptive OAuth token refresh failed against Azure AD",
                            "action": "Verify service principal client secret validity in AWS Secrets Manager.",
                            "owner": "Security Ops"
                        }
                    },
                    {
                        "alert": "P95LatencyDegradation",
                        "expr": "histogram_quantile(0.95, sum(rate(api_duration_seconds_bucket[5m])) by (le)) > 5.0",
                        "for": "5m",
                        "labels": {"severity": "P3", "team": "api-engineering"},
                        "annotations": {
                            "summary": "FinSight API P95 latency exceeded 5.0 second SLA target",
                            "action": "Investigate network latency and FinSight backend response metrics.",
                            "owner": "Marcus Wei"
                        }
                    },
                    {
                        "alert": "WorkerMemoryUtilizationHigh",
                        "expr": "container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.85",
                        "for": "3m",
                        "labels": {"severity": "P2", "team": "platform-ops"},
                        "annotations": {
                            "summary": "Container memory utilization > 85%; risk of OOM crash",
                            "action": "Evaluate garbage collection metrics; adjust heap limits.",
                            "owner": "FDE Lead"
                        }
                    },
                    {
                        "alert": "BatchBlackoutWindowViolationAttempt",
                        "expr": "blackout_window_violation_attempts_total > 0",
                        "for": "0m",
                        "labels": {"severity": "P1", "team": "sap-basis"},
                        "annotations": {
                            "summary": "Extraction scheduler attempted extraction during 01:00-04:30 blackout",
                            "action": "Immediate audit of Quartz scheduler trigger policies.",
                            "owner": "Priya Deshmukh"
                        }
                    },
                    {
                        "alert": "NetworkBandwidthCapWarning",
                        "expr": "network_egress_bytes_per_sec > 14000000",
                        "for": "2m",
                        "labels": {"severity": "P2", "team": "network-ops"},
                        "annotations": {
                            "summary": "Integration traffic exceeding 112.5 Mbps MPLS budget limit",
                            "action": "Check Gzip compression ratio; clamp extractor thread limits.",
                            "owner": "Rajesh Venkataraman"
                        }
                    },
                    {
                        "alert": "MissingExchangeRateDetected",
                        "expr": "missing_exchange_rate_events_total > 0",
                        "for": "0m",
                        "labels": {"severity": "P3", "team": "treasury-ops"},
                        "annotations": {
                            "summary": "Transaction processed using stale fallback exchange rate",
                            "action": "Request Treasury team update SAP table TCURR.",
                            "owner": "Treasury Lead"
                        }
                    },
                    {
                        "alert": "DatabaseConnectionPoolSaturated",
                        "expr": "pg_stat_activity_count > 80",
                        "for": "2m",
                        "labels": {"severity": "P2", "team": "platform-ops"},
                        "annotations": {
                            "summary": "PostgreSQL Reconciliation DB connections > 80% capacity",
                            "action": "Scale read-replicas; review connection leak logs.",
                            "owner": "Rajesh Venkataraman"
                        }
                    },
                    {
                        "alert": "RecordCountMismatchWarning",
                        "expr": "reconciliation_record_count_variance > 0",
                        "for": "5m",
                        "labels": {"severity": "P2", "team": "financial-audit"},
                        "annotations": {
                            "summary": "Record count mismatch between SAP source and FinSight destination",
                            "action": "Check DLQ for rejected records; confirm no phantom leakage.",
                            "owner": "Dr. Sanjay Kulkarni"
                        }
                    }
                ]
            }
        ]
    }

    with open(r'monitoring/alerts/prometheus-alert-rules.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(alerts, f, sort_keys=False)

    # 3. Structured Logging Specification (12 Mandatory Fields)
    logging_spec = """# Enterprise Structured Logging Specification (JSON Standard)
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
"""

    with open(r'monitoring/structured-logging-specification.md', 'w', encoding='utf-8') as f:
        f.write(logging_spec)

    # 4. Master Deliverable D6 Document
    d6_master = """# D6: Monitoring, Observability & Alerting Dashboard Specification
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Author:** Forward Deployed Engineering (FDE) Team  
**Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## 1. Executive Summary
This document defines the comprehensive telemetry, dashboard, and alerting architecture for the integration platform.
- **Grafana Dashboard:** 12-panel operational cockpit specified in `monitoring/grafana/finsight-integration-overview.json` strictly matching Appendix F (`MON-001` through `MON-012`).
- **Prometheus Alert Rules:** 16 actionable alert rules in `monitoring/alerts/prometheus-alert-rules.yaml` spanning P1 (Critical) to P4 (Informational) with assigned owners and response playbooks.
- **Structured Logging Standard:** Mandatory 12-field JSON logging standard documented in `monitoring/structured-logging-specification.md` guaranteeing cross-system distributed traceability via `correlationId`.
"""

    with open(r'monitoring/D6_Monitoring_Dashboard_Specification_v2.md', 'w', encoding='utf-8') as f:
        f.write(d6_master)

    print('Wrote all monitoring, Grafana, Prometheus alerts, and logging specs!')

if __name__ == '__main__':
    generate_monitoring()

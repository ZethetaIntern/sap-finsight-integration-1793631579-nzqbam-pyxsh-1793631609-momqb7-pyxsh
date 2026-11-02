# Technology Stack Selection and Architectural Evaluation
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Classification:** Strictly Private & Confidential  

---

## 1. Evaluation Methodology
The selection of architectural components balances enterprise reliability, low operational footprint, high throughput, zero data loss, and ease of auditability under Indian regulatory standards.

| Architectural Layer | Selected Technology | Evaluated Alternatives | Technical Justification for Selection | Rejection Rationale for Alternatives |
|:---|:---|:---|:---|:---|
| **Integration Runtime** | **Node.js 22 LTS + TypeScript 5.x** | Java Spring Boot 3, Python FastAPI, Go | Non-blocking event-driven I/O model is ideal for I/O-heavy API routing and Kafka streaming; strong TypeScript typing guarantees JSON schema contract safety; lightweight container footprint (under 120MB vs ~450MB JVM). | Spring Boot incurs higher cold-start and memory overhead in containerized clusters; Python GIL limits raw multi-threaded JSON parsing throughput at 500k-record scale. |
| **Message Broker** | **Apache Kafka 3.6 (Strimzi / Amazon MSK)** | RabbitMQ, AWS SQS/SNS, Apache Pulsar | Distributed log architecture provides true event replayability (crucial for financial auditing and reconciliation); partitioned topics enable horizontal consumer scaling; durable persistence guarantees zero message loss (RPO=0). | RabbitMQ queue-based model destroys messages upon consumption, preventing audit re-reads; SQS lacks multi-AZ message ordering guarantees across high-throughput partition keys. |
| **Audit & Reconciliation Database** | **PostgreSQL 16 (Amazon RDS Multi-AZ)** | MongoDB, DynamoDB, Redis, SQLite | ACID compliance is mandatory for financial balance ledgers and delta token tracking; robust JSONB support enables flexible storage of raw/transformed payloads; standard SQL facilitates complex reconciliation queries. | MongoDB lacks distributed transaction safety across complex multi-table accounting reconciliations; Redis is purely in-memory with durability risks. |
| **API Gateway & Ingress** | **Traefik / NGINX Ingress Controller** | Kong Gateway, AWS API Gateway, Apigee | Cloud-native, zero-downtime hot reloads; low latency TLS 1.3 termination; built-in rate-limiting, IP whitelisting, and circuit breaker middleware. | Apigee introduces significant cost and vendor lock-in; AWS API Gateway incurs high per-request costs at 500,000 requests/batch. |
| **Observability & Metrics** | **Prometheus + Grafana Enterprise** | Datadog, New Relic, Dynatrace | Open-source, self-hosted inside Indian AWS VPC ensuring zero telemetry data leakage across borders; native PromQL alerting aligns directly with enterprise Nagios/PagerDuty. | Commercial APMs violate strict corporate budget constraints and risk transmitting sensitive metadata outside India. |
| **API Specification Standard** | **OpenAPI 3.0 (YAML)** | RAML, GraphQL, gRPC | Universal enterprise standard; native support for JSON Schema, automated contract linting (Spectral), Postman collection generation, and multi-language client stub generation. | GraphQL adds unnecessary query complexity for standard batch ingestion pipelines; gRPC is not natively supported by FinSight's public REST ingestion ingress. |

---

## 2. Mandatory vs. Optional Prototype Components
- **Mandatory Production Architecture:** Apache Kafka cluster, PostgreSQL Audit Store, ODP RFC Extractor Service, Transformer Workers, Prometheus/Grafana stack, Azure AD OAuth 2.0 integration.
- **Optional Prototype Components:** In-memory mock SAP server, simulated FinSight ingestion receiver, local Docker Compose orchestration harness for rapid local validation without live SAP credentials.

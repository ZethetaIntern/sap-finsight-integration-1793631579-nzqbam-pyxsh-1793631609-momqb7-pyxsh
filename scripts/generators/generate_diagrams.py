import os

def create_diagrams():
    os.makedirs(r'architecture/diagrams/source', exist_ok=True)
    os.makedirs(r'architecture/diagrams/exports', exist_ok=True)

    # 1. C4 Level 1: System Context
    c4_l1 = """graph TB
    subgraph Enterprise ["Meridian Manufacturing Ltd. Enterprise Perimeter"]
        UserFinance["Finance Team and Plant Controllers<br/>[Person: Internal Users]"]
        ExecCFO["CFO and Executive Leadership<br/>[Person: Decision Makers]"]
        
        SAP["SAP S/4HANA 2023 FPS02<br/>[Enterprise ERP System]<br/>Core Financials, CO, MM, SD"]
        MES["Siemens Opcenter<br/>[MES System]<br/>Shopfloor Production Data"]
        Salesforce["Salesforce Enterprise<br/>[CRM System]<br/>Customer Orders and Pipeline"]
        Snowflake["Snowflake Enterprise<br/>[Enterprise Data Warehouse]<br/>Long-term Storage"]
        AzureAD["Azure Active Directory<br/>[Identity Provider]<br/>OAuth 2.0 and SSO"]
        Nagios["Nagios + Grafana<br/>[IT Monitoring]<br/>Infrastructure Telemetry"]
    end

    subgraph IntegrationBoundary ["Integration Platform Boundary"]
        IntegService["Meridian Integration Service<br/>[Integration Solution]<br/>Orchestrates ETL, Kafka, Recon and Monitoring"]
    end

    subgraph AnalyticsTarget ["Zetheta Analytics Cloud (AWS Mumbai)"]
        FinSight["Zetheta FinSight 4.2<br/>[Analytics Platform]<br/>Financial Analytics and Executive Dashboards"]
    end

    UserFinance -->|"Posts Financial Documents"| SAP
    UserFinance -->|"Accesses Operational Analytics"| FinSight
    ExecCFO -->|"Monitors 4hr Freshness Dashboards"| FinSight

    IntegService -->|"Extracts ODP Deltas and RFC BAPIs (HTTPS/mTLS, Port 44300)"| SAP
    IntegService -->|"Fetches OAuth 2.0 Client Tokens (HTTPS 443)"| AzureAD
    IntegService -->|"Streams Ingestion Micro-batches (REST/JSON, HTTPS 443)"| FinSight
    IntegService -->|"Publishes Metrics and Health Telemetry"| Nagios
    IntegService -->|"Replicates Audit Archive (Weekly)"| Snowflake
"""

    # 2. C4 Level 2: Container Diagram
    c4_l2 = """graph TB
    subgraph OnPremise ["On-Premise Tier-4 DC (Pune, Maharashtra)"]
        SAP_ERP["SAP S/4HANA 2023 FPS02<br/>[PRD Client 100]<br/>ACDOCA, BKPF, BSEG, ODP Delta Queues"]
    end

    subgraph IntegrationAWS ["Meridian Integration Platform [AWS Mumbai ap-south-1 Multi-AZ]"]
        APIGW["API Gateway and Ingress Controller<br/>[Traefik / NGINX]<br/>Rate limiting, TLS termination, Auth validation"]
        
        Scheduler["Distributed Extraction Scheduler<br/>[Node.js / Quartz Engine]<br/>Triggers 30-min ODP deltas and batch runs; respects 01:00-04:30 blackout"]
        
        Extractor["SAP Extraction Engine<br/>[Node.js / TypeScript Microservice]<br/>Manages 35 RFC pools, ODP REST/ODATA clients, cursor pagination"]
        
        KafkaBroker["Apache Kafka Message Cluster<br/>[3-Node Cluster, Strimzi/MSK]<br/>Topics: raw-extracts, transformed-events, dlq-deadletter"]
        
        TransformEngine["Data Transformation and Validation Service<br/>[Node.js / TypeScript Workers]<br/>50+ field mappings, JSON schema validator, currency conversion"]
        
        FinSightLoader["FinSight Ingestion Loader<br/>[Node.js / TypeScript Service]<br/>OAuth token manager, micro-batch poster, circuit breaker, retry engine"]
        
        ReconService["Reconciliation and Audit Engine<br/>[Node.js / Python Service]<br/>Batch and daily reconciliations, hash totals, variance reporting"]
        
        PostgreSQL["Reconciliation and Audit DB<br/>[PostgreSQL 16 Multi-AZ]<br/>Audit ledger, delta tokens, DLQ metadata, recon checkpoints"]
        
        PromGrafana["Observability Stack<br/>[Prometheus + Grafana]<br/>12-panel dashboard, 16 alert rules, scraping at 15s"]
    end

    subgraph TargetCloud ["Zetheta FinSight Cloud (AWS Mumbai ap-south-1)"]
        FinSightAPI["Zetheta FinSight 4.2 API Gateway<br/>[REST Ingestion Endpoints]<br/>DST-001 to DST-012, Rate Limit: 1000 req/min"]
    end

    SAP_ERP -->|"ODP Delta REST / RFC (Port 44300)"| Extractor
    Scheduler -->|"Triggers extraction jobs"| Extractor
    Extractor -->|"Publishes raw extracted envelopes"| KafkaBroker
    KafkaBroker -->|"Consumes raw events"| TransformEngine
    TransformEngine -->|"Validates against 28 Data Quality rules"| PostgreSQL
    TransformEngine -->|"Routes malformed records"| PostgreSQL
    TransformEngine -->|"Publishes canonical events"| KafkaBroker
    KafkaBroker -->|"Consumes transformed events"| FinSightLoader
    FinSightLoader -->|"OAuth 2.0 Bearer Ingestion (HTTPS)"| FinSightAPI
    FinSightLoader -->|"Logs load status and receipts"| PostgreSQL
    ReconService -->|"Queries extraction and load totals"| PostgreSQL
    ReconService -->|"Fetches SAP balance checksums"| SAP_ERP
    PromGrafana -->|"Scrapes Prometheus metrics"| IntegrationAWS
"""

    # 3. C4 Level 3: Extraction Engine Component
    c4_l3_ext = """graph TB
    subgraph ExtractorContainer ["SAP Extraction Service (Node.js/TypeScript)"]
        JobController["Extraction Job Controller<br/>Coordinates execution cycles and domain tasks"]
        BlackoutGuard["Blackout Window Guard<br/>Enforces 01:00-04:30 IST freeze for RGGBS000"]
        RFCPoolMgr["RFC Connection Pool Manager<br/>Caps active connections at 35 of 50 max"]
        ODPClient["ODP REST Client<br/>Queries SAP CDS Views with delta tokens"]
        CursorPaginator["Cursor Paginator<br/>Streams 5,000-row chunks with memory safety"]
        RawEnricher["Metadata Envelope Enricher<br/>Injects correlation_id, timestamp, plantCode"]
        KafkaProducer["Kafka Ingestion Producer<br/>Publishes to topic: sap.raw.{domain}"]
    end

    JobController --> BlackoutGuard
    BlackoutGuard --> RFCPoolMgr
    RFCPoolMgr --> ODPClient
    ODPClient --> CursorPaginator
    CursorPaginator --> RawEnricher
    RawEnricher --> KafkaProducer
"""

    # 4. C4 Level 3: Transformation Engine Component
    c4_l3_trans = """graph TB
    subgraph TransformContainer ["Transformation and Validation Service (Node.js/TypeScript)"]
        KafkaConsumer["Kafka Consumer Group<br/>Consumes from sap.raw.*"]
        SchemaValidator["JSON Schema Validator<br/>Validates against canonical definitions"]
        MappingRouter["Domain Mapping Router<br/>Dispatches to 1 of 10 domain transformers"]
        CurrencyEngine["Currency Normalizer<br/>Converts to Group INR using TCURR cache"]
        PeriodMapper["Fiscal Period Mapper<br/>Maps SAP 001-016 to Gregorian Calendar"]
        HierarchyFlattener["Hierarchy Flattener<br/>Flattens 7-level Cost Centre trees"]
        DLQHandler["DLQ Router<br/>Catches ERR-MAP-* errors, routes to DLQ"]
        OutboxProducer["Transformed Producer<br/>Publishes to sap.transformed.{domain}"]
    end

    KafkaConsumer --> SchemaValidator
    SchemaValidator -->|"Schema Valid"| MappingRouter
    SchemaValidator -->|"Validation Failed"| DLQHandler
    MappingRouter --> CurrencyEngine
    CurrencyEngine --> PeriodMapper
    PeriodMapper --> HierarchyFlattener
    HierarchyFlattener --> OutboxProducer
    HierarchyFlattener -->|"Mapping Exception"| DLQHandler
"""

    # 5. Data Flow 1: Real-time ODP Delta Flow
    df_odp = """flowchart TD
    SAP_ODP["SAP S/4HANA ODP Queue<br/>(Delta Token: t_now)"] -->|"1. Poll Delta (every 30m)"| Extractor["SAP Extractor Service"]
    Extractor -->|"2. Extract Envelope (5000 records)"| KafkaRaw["Kafka Topic: sap.raw.{domain}"]
    KafkaRaw -->|"3. Stream Stream Consume"| Transform["Transformation Worker"]
    Transform -->|"4. Execute Domain Mapping and Currency Conv"| Canonical["Canonical Event"]
    Canonical -->|"5. Publish Transformed"| KafkaTrans["Kafka Topic: sap.transformed.{domain}"]
    KafkaTrans -->|"6. Pull Batch"| FinSightLoader["FinSight Loader Service"]
    FinSightLoader -->|"7. Ingestion POST (HTTP 200 OK)"| FinSight["Zetheta FinSight 4.2"]
    FinSightLoader -->|"8. Commit Delta Offset"| Postgres["Recon DB Checkpoint"]
"""

    # 6. Data Flow 2: Batch Extraction Flow
    df_batch = """flowchart TD
    Scheduler["Quartz Cron Scheduler<br/>(e.g., Daily 05:00 IST)"] -->|"1. Check Blackout Guard"| Extractor["Batch Extractor Service"]
    Extractor -->|"2. RFC/BAPI Call with CompanyCode and Date Filter"| SAP["SAP PRD Core Tables (ACDOCA, BKPF)"]
    SAP -->|"3. Paginated Result Sets (Cursor chunks: 50,000)"| Extractor
    Extractor -->|"4. Chunk and Compress Envelopes"| KafkaBatch["Kafka Partitioned Topic: sap.batch.gl"]
    KafkaBatch -->|"5. Parallel Consumer Pool (Workers 1..N)"| TransformPool["Transform Workers (Multi-threaded)"]
    TransformPool -->|"6. Bulk Insert Staging"| Postgres["PostgreSQL Staging and Audit Table"]
    Postgres -->|"7. Micro-batch Dispatcher (500 recs/req)"| FinSight["FinSight Ingestion Ingress"]
"""

    # 7. Data Flow 3: Error Handling and Retry Flow
    df_error = """flowchart TD
    Incoming["Incoming Record Payload"] --> Validate{"Validation Engine"}
    Validate -->|"Fails Rules (ERR-MAP-*)"| DLQRoute["Route to Dead Letter Queue"]
    Validate -->|"Passes Rules"| Transform["Execute Transformation"]
    Transform --> Load{"Send to FinSight API"}
    Load -->|"200/201 OK"| Success["Success Ack and Commit Offset"]
    Load -->|"429 Rate Limited"| BackoffWait["Exponential Backoff with Jitter"]
    BackoffWait --> Load
    Load -->|"503 Unavailable / Network Fail"| CircuitCheck{"Circuit Breaker State?"}
    CircuitCheck -->|"Closed"| RetryQueue["Retry Topic (Max 3 attempts)"]
    RetryQueue --> Load
    CircuitCheck -->|"Open"| FastFail["Fast-Fail to Buffer Storage"]
    RetryQueue -->|"Max Retries Exceeded"| DLQRoute
    DLQRoute --> DLQStore["PostgreSQL DLQ Store and Kafka dlq-topic"]
    DLQStore --> AlertOps["Trigger PagerDuty P2 Alert"]
    DLQStore --> AdminUI["Human Exception Portal for Reprocessing"]
"""

    # 8. Data Flow 4: Reconciliation and Audit Flow
    df_recon = """flowchart TD
    Trigger["Scheduled Reconciliation Job<br/>(Batch Completion / Daily 22:00)"] --> ReconEngine["Reconciliation Engine"]
    ReconEngine -->|"1. Extract Hash Totals (SUM Debit, SUM Credit, Count)"| SAP["SAP S/4HANA (BAPI_ACC_GET_BALANCES)"]
    ReconEngine -->|"2. Extract Checkpoint Totals (Ingested count and totals)"| FinSight["FinSight Audit Query API"]
    ReconEngine -->|"3. Query Intermediate DLQ Record Count"| Postgres["Integration Recon DB"]
    SAP --> ReconEngine
    FinSight --> ReconEngine
    Postgres --> ReconEngine
    ReconEngine --> Compare{"Compare Dimension Totals:<br/>Completeness, Accuracy, Timeliness"}
    Compare -->|"Delta == 0.00"| ReconStatus["Status: RECONCILED<br/>Write signed checkpoint receipt"]
    Compare -->|"Delta > Tolerance"| BreakStatus["Status: BREAK_DETECTED<br/>Generate Discrepancy Breakdown"]
    BreakStatus --> AlertAudit["Alert Dr. Kulkarni (Internal Audit) and Finance Leads"]
    ReconStatus --> AuditReport["Store Tamper-evident Audit Ledger"]
"""

    # 9. Sequence 1: Happy Path End-to-End Sync
    seq_happy = """sequenceDiagram
    autonumber
    participant S as Scheduler
    participant E as SAP Extractor
    participant SAP as SAP S/4HANA (PRD)
    participant K as Apache Kafka
    participant T as Transform Worker
    participant L as FinSight Loader
    participant FS as Zetheta FinSight 4.2
    participant DB as PostgreSQL Recon DB

    S->>E: Trigger ODP Delta Sync (Domain: GL)
    E->>E: Check Blackout Window (Is 01:00-04:30? No)
    E->>SAP: ODP Delta Request (token: prev_token)
    SAP-->>E: Delta Records (6,247 entries) + new_token
    E->>K: Produce Raw Batch [sap.raw.gl]
    K-->>T: Consume Raw Batch
    T->>T: Validate 28 Quality Rules (All pass)
    T->>T: Normalize Currency (TCURR) and Fiscal Period
    T->>K: Produce Transformed Batch [sap.transformed.gl]
    K-->>L: Consume Transformed Batch
    L->>FS: POST /api/v1/financial/journal-entries/batch (Micro-batch: 500)
    FS-->>L: 201 Created (batchId: BATCH-GL-20260315-0930)
    L->>DB: Log Ingestion Receipt and Update Checkpoint
    L->>K: Commit Consumer Offset
"""

    # 10. Sequence 2: Error Scenario with Retry and DLQ
    seq_error = """sequenceDiagram
    autonumber
    participant K as Apache Kafka
    participant L as FinSight Loader
    participant CB as Circuit Breaker
    participant FS as Zetheta FinSight 4.2
    participant DLQ as Dead Letter Queue (Kafka/Postgres)
    participant Ops as Operations Alerting (PagerDuty)

    K->>L: Consume Transformed Message (Doc: 10000452)
    L->>CB: Execute Request through Circuit Breaker
    CB->>FS: POST /api/v1/financial/journal-entries
    FS-->>CB: 429 Too Many Requests (Retry-After: 30s)
    CB->>CB: Record Throttle Event
    L->>L: Sleep 30s + Randomized Jitter (3.4s)
    L->>FS: Retry Attempt 1: POST /api/v1/financial/journal-entries
    FS-->>CB: 503 Service Unavailable (FinSight Overload)
    CB->>CB: Increment Failure Count (Threshold: 5)
    L->>L: Exponential Backoff (60s)
    L->>FS: Retry Attempt 2: POST /api/v1/financial/journal-entries
    FS-->>CB: 503 Service Unavailable
    CB->>CB: Failure Threshold Exceeded -> State = OPEN
    L->>DLQ: Route to DLQ (ERR-LOAD-002, attempts: 3)
    DLQ->>Ops: Emit PagerDuty P2 Alert (FinSight API 503 Circuit Open)
    L->>K: Commit Offset (Unblock partition consumer)
"""

    # 11. Sequence 3: Reconciliation Mismatch Resolution
    seq_recon = """sequenceDiagram
    autonumber
    participant R as Reconciliation Engine
    participant SAP as SAP S/4HANA (BAPI_ACC_GET_BALANCES)
    participant FS as FinSight Audit API
    participant DB as Recon DB
    participant Aud as Internal Audit (Dr. Kulkarni)

    R->>SAP: Query Batch Debit/Credit Total (PostingDate: 2026-03-15)
    SAP-->>R: Source Total: INR 24,17,89,342.30 (Count: 6,247)
    R->>FS: Query Ingested Total (PostingDate: 2026-03-15)
    FS-->>R: Target Total: INR 24,17,89,340.80 (Count: 6,243)
    R->>DB: Query Active DLQ for Batch
    DB-->>R: DLQ Count: 4 Records (Variance Amount: INR 1.50)
    R->>R: Calculate Variance (INR 1.50 matches DLQ line items exactly)
    R->>R: Status: RECONCILED_WITH_EXCEPTION (No Phantom Leakage)
    R->>DB: Persist Batch Recon Report
    R->>Aud: Publish Automated Reconciliation Report
"""

    files = {
        'DGM_C4_SystemContext.mermaid': c4_l1,
        'DGM_C4_Container.mermaid': c4_l2,
        'DGM_C4_Component_Extraction.mermaid': c4_l3_ext,
        'DGM_C4_Component_Transformation.mermaid': c4_l3_trans,
        'DGM_DataFlow_ODP_Delta.mermaid': df_odp,
        'DGM_DataFlow_Batch_Extraction.mermaid': df_batch,
        'DGM_DataFlow_Error_Retry_DLQ.mermaid': df_error,
        'DGM_DataFlow_Reconciliation_Audit.mermaid': df_recon,
        'DGM_Sequence_HappyPath_Sync.mermaid': seq_happy,
        'DGM_Sequence_Error_DLQ.mermaid': seq_error,
        'DGM_Sequence_Recon_Mismatch.mermaid': seq_recon,
    }

    for fname, content in files.items():
        with open(os.path.join(r'architecture/diagrams/source', fname), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Wrote {fname}')

    # Create Draw.io XML files
    drawio_template = '''<mxfile host="app.diagrams.net" modified="2026-11-02T12:00:00.000Z" agent="Antigravity" version="24.0.0" type="device">
  <diagram id="{diagram_id}" name="{diagram_name}">
    <mxGraphModel dx="1422" dy="798" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=20;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="280" y="20" width="600" height="40" as="geometry" />
        </mxCell>
        <mxCell id="box_sap" value="SAP S/4HANA 2023 FPS02&#xa;[Enterprise ERP System]&#xa;ACDOCA, BKPF, BSEG, ODP Queues" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="80" y="120" width="220" height="100" as="geometry" />
        </mxCell>
        <mxCell id="box_integ" value="Meridian Integration Platform&#xa;[Node.js / Kafka / PostgreSQL / ODP]&#xa;Extraction, Transformation, Recon, Monitoring" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="440" y="120" width="280" height="100" as="geometry" />
        </mxCell>
        <mxCell id="box_finsight" value="Zetheta FinSight 4.2&#xa;[Target Financial Analytics]&#xa;Executive Dashboards &amp; KPIs" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="840" y="120" width="220" height="100" as="geometry" />
        </mxCell>
        <mxCell id="edge1" value="ODP Delta / RFC (Port 44300)&#xa;30-min sync, max 35 RFCs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" edge="1" parent="1" source="box_sap" target="box_integ">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge2" value="REST/JSON HTTPS (Port 443)&#xa;OAuth 2.0 Bearer, Micro-batches" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" edge="1" parent="1" source="box_integ" target="box_finsight">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

    with open(r'architecture/diagrams/source/DGM_C4_SystemContext.drawio', 'w', encoding='utf-8') as f:
        f.write(drawio_template.format(diagram_id="c4_l1", diagram_name="System Context", title="Meridian Manufacturing - SAP S/4HANA to FinSight C4 System Context"))

    with open(r'architecture/diagrams/source/DGM_C4_Container.drawio', 'w', encoding='utf-8') as f:
        f.write(drawio_template.format(diagram_id="c4_l2", diagram_name="Container Diagram", title="Meridian Integration Platform - C4 Container Diagram"))

    with open(r'architecture/diagrams/source/DGM_Network_Topology.drawio', 'w', encoding='utf-8') as f:
        f.write(drawio_template.format(diagram_id="net_topo", diagram_name="Network Topology", title="Meridian Hybrid Network Topology - Cisco SD-WAN to AWS VPC"))

    print('Wrote Draw.io XML files!')

    # Create SVG representation for visual exports
    def create_svg(title, subtitle, filename):
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500" width="100%" height="100%">
  <rect width="1000" height="500" fill="#f8fafc"/>
  <text x="500" y="45" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#0f172a" text-anchor="middle">{title}</text>
  <text x="500" y="75" font-family="Arial, sans-serif" font-size="14" fill="#64748b" text-anchor="middle">{subtitle}</text>
  
  <!-- SAP Node -->
  <rect x="50" y="150" width="240" height="180" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="170" y="190" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1e3a8a" text-anchor="middle">SAP S/4HANA 2023</text>
  <text x="170" y="215" font-family="Arial, sans-serif" font-size="12" fill="#3b82f6" text-anchor="middle">[Enterprise Core ERP]</text>
  <text x="170" y="245" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">ACDOCA, BKPF, BSEG</text>
  <text x="170" y="265" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">ODP Delta Framework</text>
  <text x="170" y="285" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">Hinjawadi DC, Pune</text>

  <!-- Integration Node -->
  <rect x="370" y="130" width="260" height="220" rx="12" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>
  <text x="500" y="170" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#14532d" text-anchor="middle">Integration Platform</text>
  <text x="500" y="195" font-family="Arial, sans-serif" font-size="12" fill="#16a34a" text-anchor="middle">[Node.js / Kafka / Postgres]</text>
  <text x="500" y="225" font-family="Arial, sans-serif" font-size="11" fill="#334155" text-anchor="middle">• ODP Delta Extractor</text>
  <text x="500" y="245" font-family="Arial, sans-serif" font-size="11" fill="#334155" text-anchor="middle">• Kafka Messaging &amp; DLQ</text>
  <text x="500" y="265" font-family="Arial, sans-serif" font-size="11" fill="#334155" text-anchor="middle">• 50+ Domain Mappings</text>
  <text x="500" y="285" font-family="Arial, sans-serif" font-size="11" fill="#334155" text-anchor="middle">• Reconciliation Engine</text>
  <text x="500" y="305" font-family="Arial, sans-serif" font-size="11" fill="#334155" text-anchor="middle">• Prometheus/Grafana Stack</text>

  <!-- FinSight Node -->
  <rect x="710" y="150" width="240" height="180" rx="12" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="830" y="190" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#78350f" text-anchor="middle">Zetheta FinSight 4.2</text>
  <text x="830" y="215" font-family="Arial, sans-serif" font-size="12" fill="#d97706" text-anchor="middle">[Financial Analytics Platform]</text>
  <text x="830" y="245" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">REST Ingestion APIs</text>
  <text x="830" y="265" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">OAuth 2.0 Client Credentials</text>
  <text x="830" y="285" font-family="Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">AWS Mumbai (ap-south-1)</text>

  <!-- Connectors -->
  <line x1="290" y1="240" x2="370" y2="240" stroke="#0284c7" stroke-width="3" stroke-dasharray="6,4"/>
  <polygon points="368,235 378,240 368,245" fill="#0284c7"/>
  <text x="330" y="225" font-family="Arial, sans-serif" font-size="10" fill="#0369a1" text-anchor="middle">ODP / RFC</text>

  <line x1="630" y1="240" x2="710" y2="240" stroke="#059669" stroke-width="3"/>
  <polygon points="708,235 718,240 708,245" fill="#059669"/>
  <text x="670" y="225" font-family="Arial, sans-serif" font-size="10" fill="#047857" text-anchor="middle">HTTPS REST</text>

  <!-- Footer Banner -->
  <rect x="50" y="400" width="900" height="50" rx="8" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="500" y="430" font-family="Arial, sans-serif" font-size="12" fill="#475569" text-anchor="middle">Target Data Freshness: &lt;= 4 Hours | Peak Throughput: 500,000 GL records / 2 Hours | Zero Financial Breaks</text>
</svg>'''
        with open(os.path.join(r'architecture/diagrams/exports', filename), 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f'Wrote export {filename}')

    create_svg("Meridian Manufacturing Ltd. - System Context Diagram (C4 Level 1)", "Enterprise System Boundaries and Cross-Platform Integration", "DGM_C4_SystemContext.svg")
    create_svg("Meridian Integration Platform - Container Diagram (C4 Level 2)", "Internal Microservices, Kafka Message Broker, and Reconciliation Storage", "DGM_C4_Container.svg")
    create_svg("Real-Time ODP Delta Data Flow Architecture", "30-Minute Delta Extraction from SAP ACDOCA to FinSight Ingestion", "DGM_DataFlow_ODP_Delta.svg")
    create_svg("End-to-End Happy Path Sync Sequence", "Extraction, Transformation, Validation, and Ingestion Sequence", "DGM_Sequence_HappyPath_Sync.svg")
    create_svg("Resilience &amp; Failure Recovery Sequence", "Exponential Backoff, Circuit Breaker Tripping, and Dead Letter Queue", "DGM_Sequence_Error_DLQ.svg")

if __name__ == '__main__':
    create_diagrams()

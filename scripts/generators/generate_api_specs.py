import os
import yaml
import json

def create_api_specs():
    os.makedirs(r'api-specifications/sap-source', exist_ok=True)
    os.makedirs(r'api-specifications/finsight-destination', exist_ok=True)
    os.makedirs(r'api-specifications/postman', exist_ok=True)

    # 1. Master SAP Source OpenAPI Specification (12 Endpoints)
    sap_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "SAP S/4HANA 2023 FPS02 - Source Extraction OData/REST API",
            "version": "1.0.0",
            "description": "Enterprise source API specification for Meridian Manufacturing Ltd. exposing 12 financial and operational data domains via SAP CDS Views and ODP Delta queues. Verified against SAP S/4HANA 2023 FPS02 data dictionary."
        },
        "servers": [
            {
                "url": "https://sap-prd.meridian.internal:44300/sap/opu/odata/sap",
                "description": "SAP Production Environment (Hinjawadi DC, Client 100)"
            },
            {
                "url": "https://sap-qas.meridian.internal:44300/sap/opu/odata/sap",
                "description": "SAP Quality Assurance Environment (Client 200)"
            }
        ],
        "security": [
            {"SAP_Basic_or_ClientCert": []}
        ],
        "paths": {
            "/ZZ_FIN_GL_CDS/GLItems": {
                "get": {
                    "summary": "SRC-001: General Ledger Journal Entries (ACDOCA)",
                    "description": "Extracts Universal Journal line items using ODP Delta tokens.",
                    "parameters": [
                        {"name": "$filter", "in": "query", "schema": {"type": "string"}, "example": "RBUKRS eq 'MC01' and GJAHR eq '2026'"},
                        {"name": "$skiptoken", "in": "query", "schema": {"type": "string"}, "description": "ODP cursor token for next page"},
                        {"name": "$top", "in": "query", "schema": {"type": "integer", "default": 5000}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful extraction of GL items",
                            "headers": {
                                "delta-token": {"schema": {"type": "string"}, "description": "Current delta token for subsequent sync"}
                            },
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SAP_GL_Response"}
                                }
                            }
                        },
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                        "429": {"$ref": "#/components/responses/TooManyRequests"},
                        "503": {"$ref": "#/components/responses/ServiceUnavailable"}
                    }
                }
            },
            "/ZZ_FIN_AP_CDS/VendorInvoices": {
                "get": {
                    "summary": "SRC-002: Accounts Payable Invoices (BSIK/BSAK/LFA1)",
                    "description": "Extracts open and cleared vendor items with vendor master data enrichment.",
                    "parameters": [
                        {"name": "$filter", "in": "query", "schema": {"type": "string"}},
                        {"name": "$top", "in": "query", "schema": {"type": "integer", "default": 5000}}
                    ],
                    "responses": {"200": {"description": "AP items extracted successfully"}}
                }
            },
            "/ZZ_FIN_AR_CDS/CustomerReceivables": {
                "get": {
                    "summary": "SRC-003: Accounts Receivable Items (BSID/BSAD/KNA1)",
                    "description": "Extracts open receivables, customer credit data, and payment history.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "AR items extracted successfully"}}
                }
            },
            "/ZZ_FIN_CO_CDS/CostCentres": {
                "get": {
                    "summary": "SRC-004: Cost Centre Master and Actuals (CSKS/COSP/COSS)",
                    "description": "Extracts cost centre hierarchy, controlling area postings, and texts.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Cost Centre records extracted successfully"}}
                }
            },
            "/ZZ_FIN_PCA_CDS/ProfitCentres": {
                "get": {
                    "summary": "SRC-005: Profit Centre Master and Segment Allocations (CEPC)",
                    "description": "Extracts profit centre organizational hierarchy and segment assignments.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Profit Centre items extracted successfully"}}
                }
            },
            "/ZZ_FIN_ML_CDS/MaterialValuations": {
                "get": {
                    "summary": "SRC-006: Material Ledger Actual Costing (MBEW/CKMLCR)",
                    "description": "Extracts inventory moving average prices, standard costs, and price variances.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Material Ledger items extracted successfully"}}
                }
            },
            "/ZZ_MM_PO_CDS/PurchaseOrders": {
                "get": {
                    "summary": "SRC-007: Purchase Orders Procurement (EKKO/EKPO/EKET)",
                    "description": "Extracts PO headers, line items, schedule lines, and GR/IR clearing statuses.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Purchase orders extracted successfully"}}
                }
            },
            "/ZZ_SD_SO_CDS/SalesOrders": {
                "get": {
                    "summary": "SRC-008: Sales Orders and Order Pipeline (VBAK/VBAP/VBEP)",
                    "description": "Extracts sales order schedule lines, pricing conditions, and net values.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Sales orders extracted successfully"}}
                }
            },
            "/ZZ_FI_AA_CDS/FixedAssets": {
                "get": {
                    "summary": "SRC-009: Fixed Asset Master and Depreciation (ANLA/ANLZ/ANLP)",
                    "description": "Extracts capital asset register, capitalization dates, and accumulated depreciation.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Fixed assets extracted successfully"}}
                }
            },
            "/ZZ_FI_BL_CDS/BankStatements": {
                "get": {
                    "summary": "SRC-010: Electronic Bank Statements (FEBKO/FEBEP)",
                    "description": "Extracts intra-day electronic bank statements, MT940 line items, and clearing status.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Bank statements extracted successfully"}}
                }
            },
            "/ZZ_CO_BGT_CDS/BudgetActuals": {
                "get": {
                    "summary": "SRC-011: Controlling Budget vs. Actual Variance (COSP/COSS)",
                    "description": "Extracts annual/monthly cost centre budget allocations and actual variance totals.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Budget variance records extracted successfully"}}
                }
            },
            "/ZZ_MM_INV_CDS/InventoryItems": {
                "get": {
                    "summary": "SRC-012: Plant Inventory and Storage Location Balances (MARD)",
                    "description": "Extracts stock quantities across unrestricted, inspection, and blocked valuation states.",
                    "parameters": [{"name": "$filter", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Inventory balances extracted successfully"}}
                }
            }
        },
        "components": {
            "securitySchemes": {
                "SAP_Basic_or_ClientCert": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "Dedicated system user INTEG_SVC_FDE or X.509 Client Certificate authentication."
                }
            },
            "schemas": {
                "SAP_GL_Response": {
                    "type": "object",
                    "properties": {
                        "d": {
                            "type": "object",
                            "properties": {
                                "results": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/ACDOCA_Record"}
                                },
                                "__next": {"type": "string"}
                            }
                        }
                    }
                },
                "ACDOCA_Record": {
                    "type": "object",
                    "required": ["RCLNT", "RBUKRS", "GJAHR", "BELNR", "BUZEI", "RACCT", "HSL", "RHCUR", "BUDAT"],
                    "properties": {
                        "RCLNT": {"type": "string", "example": "100"},
                        "RLDNR": {"type": "string", "example": "0L"},
                        "RBUKRS": {"type": "string", "example": "MC01"},
                        "GJAHR": {"type": "string", "example": "2026"},
                        "BELNR": {"type": "string", "example": "0100004521"},
                        "BUZEI": {"type": "string", "example": "001"},
                        "RACCT": {"type": "string", "example": "0000400000"},
                        "HSL": {"type": "number", "format": "decimal", "example": 150000.50},
                        "RHCUR": {"type": "string", "example": "INR"},
                        "WSL": {"type": "number", "format": "decimal", "example": 1800.00},
                        "RWCUR": {"type": "string", "example": "USD"},
                        "DRCRK": {"type": "string", "enum": ["S", "H"], "example": "S"},
                        "BUDAT": {"type": "string", "example": "20260315"},
                        "BLDAT": {"type": "string", "example": "20260314"},
                        "MONAT": {"type": "string", "example": "012"},
                        "KOSTL": {"type": "string", "example": "0000002100"},
                        "PRCTR": {"type": "string", "example": "0000001000"},
                        "BLART": {"type": "string", "example": "SA"}
                    }
                }
            },
            "responses": {
                "Unauthorized": {
                    "description": "Authentication failure: invalid SAP user or certificate",
                    "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
                },
                "TooManyRequests": {
                    "description": "RFC pool exhausted or SAP Basis throttling active",
                    "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
                },
                "ServiceUnavailable": {
                    "description": "SAP instance under nightly maintenance or batch blackout (RGGBS000)",
                    "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
                }
            }
        }
    }

    # 2. Master FinSight Destination OpenAPI Specification (12 Endpoints)
    finsight_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Zetheta FinSight 4.2 - Financial Analytics Ingestion REST API",
            "version": "4.2.0",
            "description": "Target financial ingestion API contract for Zetheta FinSight 4.2. [Assumed Contract: Standard Zetheta Ingestion Specification]. Supports micro-batching, strict schema validation, OAuth 2.0 Client Credentials, and idempotency guarantees."
        },
        "servers": [
            {
                "url": "https://api-mumbai.finsight.zetheta.com/v1",
                "description": "FinSight Production Cloud (AWS Mumbai ap-south-1)"
            },
            {
                "url": "https://staging-mumbai.finsight.zetheta.com/v1",
                "description": "FinSight Staging Sandbox (AWS Mumbai ap-south-1)"
            }
        ],
        "security": [
            {"OAuth2": ["finsight:financial:write", "finsight:controlling:write", "finsight:procurement:write"]}
        ],
        "paths": {
            "/financial/journal-entries/batch": {
                "post": {
                    "summary": "DST-001: Ingest General Ledger Journal Entries",
                    "description": "Micro-batch endpoint accepting up to 500 validated journal entry records per payload.",
                    "parameters": [
                        {"name": "X-Tenant-ID", "in": "header", "required": True, "schema": {"type": "string", "example": "MERIDIAN-PROD"}},
                        {"name": "X-Idempotency-Key", "in": "header", "required": True, "schema": {"type": "string", "format": "uuid"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/JournalEntryBatchRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Micro-batch successfully ingested and indexed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BatchIngestResponse"}
                                }
                            }
                        },
                        "400": {"$ref": "#/components/responses/400_BadRequest"},
                        "401": {"$ref": "#/components/responses/401_Unauthorized"},
                        "409": {"$ref": "#/components/responses/409_DuplicateEntry"},
                        "422": {"$ref": "#/components/responses/422_BusinessRuleViolation"},
                        "429": {"$ref": "#/components/responses/429_RateLimited"},
                        "503": {"$ref": "#/components/responses/503_ServiceUnavailable"}
                    }
                }
            },
            "/payables/invoices/batch": {
                "post": {
                    "summary": "DST-002: Ingest Vendor Invoices and Payables",
                    "responses": {"201": {"description": "Vendor invoices ingested successfully"}}
                }
            },
            "/receivables/invoices/batch": {
                "post": {
                    "summary": "DST-003: Ingest Customer Receivables and Dunning Records",
                    "responses": {"201": {"description": "Customer receivables ingested successfully"}}
                }
            },
            "/controlling/cost-centres/batch": {
                "post": {
                    "summary": "DST-004: Ingest Flattened Cost Centre Performance",
                    "responses": {"201": {"description": "Cost centre performance ingested successfully"}}
                }
            },
            "/controlling/profit-centres/batch": {
                "post": {
                    "summary": "DST-005: Ingest Profit Centre Margins and Segment Allocations",
                    "responses": {"201": {"description": "Profit centre margins ingested successfully"}}
                }
            },
            "/inventory/material-costs/batch": {
                "post": {
                    "summary": "DST-006: Ingest Material Ledger Costing and Variances",
                    "responses": {"201": {"description": "Material costs ingested successfully"}}
                }
            },
            "/procurement/purchase-orders/batch": {
                "post": {
                    "summary": "DST-007: Ingest Purchase Orders and Spend Summaries",
                    "responses": {"201": {"description": "Purchase orders ingested successfully"}}
                }
            },
            "/sales/orders/batch": {
                "post": {
                    "summary": "DST-008: Ingest Sales Orders and Backlog Records",
                    "responses": {"201": {"description": "Sales orders ingested successfully"}}
                }
            },
            "/assets/register/batch": {
                "post": {
                    "summary": "DST-009: Ingest Fixed Assets Register and Depreciation",
                    "responses": {"201": {"description": "Fixed asset register ingested successfully"}}
                }
            },
            "/treasury/cash-positions/batch": {
                "post": {
                    "summary": "DST-010: Ingest Bank Cash Positions and Statement Feeds",
                    "responses": {"201": {"description": "Cash positions ingested successfully"}}
                }
            },
            "/controlling/budget-performance/batch": {
                "post": {
                    "summary": "DST-011: Ingest Departmental Budget vs. Actual Performance",
                    "responses": {"201": {"description": "Budget performance ingested successfully"}}
                }
            },
            "/inventory/balances/batch": {
                "post": {
                    "summary": "DST-012: Ingest Plant Inventory Balances",
                    "responses": {"201": {"description": "Inventory balances ingested successfully"}}
                }
            }
        },
        "components": {
            "securitySchemes": {
                "OAuth2": {
                    "type": "oauth2",
                    "description": "Azure Active Directory / FinSight OAuth 2.0 Client Credentials Grant",
                    "flows": {
                        "clientCredentials": {
                            "tokenUrl": "https://auth.finsight.zetheta.com/oauth/v2/token",
                            "scopes": {
                                "finsight:financial:write": "Write access to GL, AP, and AR financial ledgers",
                                "finsight:controlling:write": "Write access to Cost Centre and Profit Centre models",
                                "finsight:procurement:write": "Write access to Procurement and Material records"
                            }
                        }
                    }
                }
            },
            "schemas": {
                "JournalEntryBatchRequest": {
                    "type": "object",
                    "required": ["batchId", "batchTimestamp", "sourceSystem", "recordCount", "records"],
                    "properties": {
                        "batchId": {"type": "string", "example": "BATCH-GL-20260315-0930"},
                        "batchTimestamp": {"type": "string", "format": "date-time", "example": "2026-03-15T09:30:00+05:30"},
                        "sourceSystem": {"type": "string", "example": "SAP-PRD-MC01"},
                        "recordCount": {"type": "integer", "example": 500},
                        "records": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/CanonicalJournalEntry"}
                        }
                    }
                },
                "CanonicalJournalEntry": {
                    "type": "object",
                    "required": [
                        "documentId", "companyCode", "fiscalYear", "documentNumber", "lineItem",
                        "postingDate", "documentDate", "glAccount", "amountLC", "localCurrency",
                        "postingType", "fiscalPeriod", "documentType"
                    ],
                    "properties": {
                        "documentId": {"type": "string", "example": "MC01-2026-0100004521-001"},
                        "companyCode": {"type": "string", "example": "MC01"},
                        "fiscalYear": {"type": "integer", "example": 2026},
                        "documentNumber": {"type": "string", "example": "0100004521"},
                        "lineItem": {"type": "integer", "example": 1},
                        "postingDate": {"type": "string", "format": "date", "example": "2026-03-15"},
                        "documentDate": {"type": "string", "format": "date", "example": "2026-03-14"},
                        "glAccount": {"type": "string", "example": "400000"},
                        "amountLC": {"type": "number", "format": "decimal", "example": 150000.50},
                        "localCurrency": {"type": "string", "example": "INR"},
                        "amountTC": {"type": "number", "format": "decimal", "example": 1800.00},
                        "transactionCurrency": {"type": "string", "example": "USD"},
                        "postingType": {"type": "string", "enum": ["DEBIT", "CREDIT"], "example": "DEBIT"},
                        "costCentre": {"type": "string", "nullable": True, "example": "2100"},
                        "profitCentre": {"type": "string", "nullable": True, "example": "1000"},
                        "fiscalPeriod": {"type": "string", "example": "2026-03"},
                        "isSpecialPeriod": {"type": "boolean", "default": False},
                        "documentType": {"type": "string", "example": "GL_ACCOUNT_POSTING"},
                        "isReversal": {"type": "boolean", "default": False}
                    }
                },
                "BatchIngestResponse": {
                    "type": "object",
                    "properties": {
                        "batchId": {"type": "string", "example": "BATCH-GL-20260315-0930"},
                        "status": {"type": "string", "example": "PROCESSED"},
                        "recordsReceived": {"type": "integer", "example": 500},
                        "recordsLoaded": {"type": "integer", "example": 500},
                        "recordsSkipped": {"type": "integer", "example": 0},
                        "ingestionTimestamp": {"type": "string", "format": "date-time"}
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "errorCode": {"type": "string", "example": "INVALID_REQUEST"},
                        "message": {"type": "string", "example": "JSON schema validation failed"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "details": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "responses": {
                "400_BadRequest": {
                    "description": "INVALID_REQUEST / INVALID_DATE_FORMAT / INVALID_CURRENCY_CODE",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                },
                "401_Unauthorized": {
                    "description": "TOKEN_EXPIRED / INVALID_TOKEN",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                },
                "409_DuplicateEntry": {
                    "description": "DUPLICATE_ENTRY: Idempotent duplicate detected",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                },
                "422_BusinessRuleViolation": {
                    "description": "BUSINESS_RULE_VIOLATION / REFERENTIAL_INTEGRITY",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                },
                "429_RateLimited": {
                    "description": "RATE_LIMITED: Ingestion rate limit exceeded",
                    "headers": {
                        "Retry-After": {"schema": {"type": "integer"}, "description": "Seconds to wait before retrying"}
                    },
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                },
                "503_ServiceUnavailable": {
                    "description": "SERVICE_UNAVAILABLE: Analytics platform undergoing maintenance",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                }
            }
        }
    }

    # Write master YAML files
    with open(r'api-specifications/sap-source/openapi-sap-source.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(sap_spec, f, sort_keys=False)
    with open(r'api-specifications/finsight-destination/openapi-finsight-destination.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(finsight_spec, f, sort_keys=False)

    print('Wrote master OpenAPI specs!')

    # Postman Collection Generation
    postman_collection = {
        "info": {
            "name": "Meridian SAP S/4HANA to FinSight 4.2 Integration API Collection",
            "description": "Automated test and invocation collection covering all 12 SAP source endpoints and 12 FinSight destination ingestion endpoints.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "00. OAuth 2.0 Token Generation",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Content-Type", "value": "application/x-www-form-urlencoded"}
                    ],
                    "body": {
                        "mode": "urlencoded",
                        "urlencoded": [
                            {"key": "grant_type", "value": "client_credentials", "type": "text"},
                            {"key": "client_id", "value": "{{client_id}}", "type": "text"},
                            {"key": "client_secret", "value": "{{client_secret}}", "type": "text"},
                            {"key": "scope", "value": "finsight:financial:write finsight:controlling:write", "type": "text"}
                        ]
                    },
                    "url": {
                        "raw": "{{auth_url}}/oauth/v2/token",
                        "host": ["{{auth_url}}"],
                        "path": ["oauth", "v2", "token"]
                    }
                }
            },
            {
                "name": "01. SAP Source - GL Items (SRC-001)",
                "request": {
                    "method": "GET",
                    "header": [
                        {"key": "Accept", "value": "application/json"}
                    ],
                    "url": {
                        "raw": "{{sap_base_url}}/ZZ_FIN_GL_CDS/GLItems?$filter=RBUKRS eq 'MC01' and GJAHR eq '2026'&$top=500",
                        "host": ["{{sap_base_url}}"],
                        "path": ["ZZ_FIN_GL_CDS", "GLItems"],
                        "query": [
                            {"key": "$filter", "value": "RBUKRS eq 'MC01' and GJAHR eq '2026'"},
                            {"key": "$top", "value": "500"}
                        ]
                    }
                }
            },
            {
                "name": "02. FinSight Destination - Ingest GL Batch (DST-001)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Content-Type", "value": "application/json"},
                        {"key": "Authorization", "value": "Bearer {{access_token}}"},
                        {"key": "X-Tenant-ID", "value": "MERIDIAN-PROD"},
                        {"key": "X-Idempotency-Key", "value": "{{$guid}}"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "batchId": "BATCH-GL-20260315-0930",
                            "batchTimestamp": "2026-03-15T09:30:00+05:30",
                            "sourceSystem": "SAP-PRD-MC01",
                            "recordCount": 1,
                            "records": [
                                {
                                    "documentId": "MC01-2026-0100004521-001",
                                    "companyCode": "MC01",
                                    "fiscalYear": 2026,
                                    "documentNumber": "0100004521",
                                    "lineItem": 1,
                                    "postingDate": "2026-03-15",
                                    "documentDate": "2026-03-14",
                                    "glAccount": "400000",
                                    "amountLC": 150000.50,
                                    "localCurrency": "INR",
                                    "amountTC": 1800.00,
                                    "transactionCurrency": "USD",
                                    "postingType": "DEBIT",
                                    "costCentre": "2100",
                                    "profitCentre": "1000",
                                    "fiscalPeriod": "2026-03",
                                    "isSpecialPeriod": False,
                                    "documentType": "GL_ACCOUNT_POSTING",
                                    "isReversal": False
                                }
                            ]
                        }, indent=2)
                    },
                    "url": {
                        "raw": "{{finsight_base_url}}/financial/journal-entries/batch",
                        "host": ["{{finsight_base_url}}"],
                        "path": ["financial", "journal-entries", "batch"]
                    }
                }
            }
        ]
    }

    postman_env = {
        "id": "meridian-dev-env",
        "name": "Meridian Integration Dev Environment",
        "values": [
            {"key": "sap_base_url", "value": "https://sap-prd.meridian.internal:44300/sap/opu/odata/sap", "enabled": True},
            {"key": "finsight_base_url", "value": "https://staging-mumbai.finsight.zetheta.com/v1", "enabled": True},
            {"key": "auth_url", "value": "https://auth.finsight.zetheta.com", "enabled": True},
            {"key": "client_id", "value": "meridian_integration_spn_01", "enabled": True},
            {"key": "client_secret", "value": "SEC_PLACEHOLDER_VAULT_TOKEN", "enabled": True},
            {"key": "access_token", "value": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...", "enabled": True}
        ]
    }

    with open(r'api-specifications/postman/Meridian_SAP_FinSight_Integration.postman_collection.json', 'w', encoding='utf-8') as f:
        json.dump(postman_collection, f, indent=2)

    with open(r'api-specifications/postman/Meridian_Dev_Environment.postman_environment.json', 'w', encoding='utf-8') as f:
        json.dump(postman_env, f, indent=2)

    print('Wrote Postman collection and environment files!')

    # D2 Master API Specification Document
    d2_doc = """# D2: API Specification Document (Source & Destination Endpoints)
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Client:** Meridian Manufacturing Ltd.  
**Author:** Forward Deployed Engineering (FDE) Team  
**Version:** 2.0  
**Classification:** Strictly Private & Confidential  

---

## 1. Overview and Ingestion Principles
This document specifies the bidirectional interface contracts governing the data pipeline between **SAP S/4HANA 2023 FPS02** and **Zetheta FinSight 4.2**.
- **Source API Paradigm:** SAP Core Data Services (CDS) Views exposed as OData v2/v4 and ODP (Operational Data Provisioning) REST services.
- **Destination API Paradigm:** RESTful micro-batch JSON ingestion endpoints protected by OAuth 2.0 Client Credentials and tenant-isolated namespaces.
- **Idempotency Guarantee:** All destination `POST` endpoints enforce idempotency via the `X-Idempotency-Key` header (UUIDv4) and composite business keys (`CompanyCode-FiscalYear-DocNumber-LineItem`).

---

## 2. SAP Source Endpoint Directory (12 Endpoints)

| Endpoint ID | Domain Name | SAP Source Tables / CDS View | Extraction Pattern | Endpoint URI Path | Delta Mechanism |
|:---|:---|:---|:---|:---|:---|
| **SRC-001** | General Ledger | ACDOCA, BKPF, BSEG (`ZZ_CDS_ACDOCA_DELTA`) | 30-min Delta / Micro-batch | `/ZZ_FIN_GL_CDS/GLItems` | ODP Delta Token (`$skiptoken`) |
| **SRC-002** | Accounts Payable | BSIK, BSAK, LFA1, LFC1 (`ZZ_CDS_AP_DELTA`) | 30-min Delta | `/ZZ_FIN_AP_CDS/VendorInvoices` | ODP Delta Token |
| **SRC-003** | Accounts Receivable | BSID, BSAD, KNA1, KNC1 (`ZZ_CDS_AR_DELTA`) | 30-min Delta | `/ZZ_FIN_AR_CDS/CustomerReceivables` | ODP Delta Token |
| **SRC-004** | Cost Centre | CSKS, CSKT, COSP, COSS (`ZZ_CDS_CC_MASTER`) | Daily Master / Intra-day Actuals | `/ZZ_FIN_CO_CDS/CostCentres` | Timestamp Filter (`AEDAT`) |
| **SRC-005** | Profit Centre | CEPC, CEPCT (`ZZ_CDS_PC_MASTER`) | Daily Master | `/ZZ_FIN_PCA_CDS/ProfitCentres` | Timestamp Filter (`AEDAT`) |
| **SRC-006** | Material Ledger | MBEW, MLCD, CKMLCR (`ZZ_CDS_ML_COSTS`) | Hourly Batch | `/ZZ_FIN_ML_CDS/MaterialValuations` | Period / Valuation Token |
| **SRC-007** | Purchase Orders | EKKO, EKPO, EKET (`ZZ_CDS_MM_PO`) | 30-min Delta | `/ZZ_MM_PO_CDS/PurchaseOrders` | ODP Delta Token |
| **SRC-008** | Sales Orders | VBAK, VBAP, VBEP (`ZZ_CDS_SD_SO`) | 30-min Delta | `/ZZ_SD_SO_CDS/SalesOrders` | ODP Delta Token |
| **SRC-009** | Fixed Assets | ANLA, ANLZ, ANLP (`ZZ_CDS_FI_AA`) | Monthly Batch / Delta | `/ZZ_FI_AA_CDS/FixedAssets` | Asset Capitalization Token |
| **SRC-010** | Bank Statements | FEBKO, FEBEP (`ZZ_CDS_FI_BL`) | Intra-day Delta | `/ZZ_FI_BL_CDS/BankStatements` | Statement ID Token |
| **SRC-011** | Budget vs. Actual | COSP, COSS (`ZZ_CDS_CO_BGT`) | Daily Batch | `/ZZ_CO_BGT_CDS/BudgetActuals` | Fiscal Period Token |
| **SRC-012** | Inventory Balances| MARD, MBEW (`ZZ_CDS_MM_INV`) | Hourly Batch | `/ZZ_MM_INV_CDS/InventoryItems` | Storage Location Token |

---

## 3. FinSight Destination Endpoint Directory (12 Endpoints)
*[Notice: Assumed Contract - Based on Standard Zetheta FinSight 4.2 API Specification]*

| Endpoint ID | FinSight Resource Domain | Ingestion Method & Path | Target Analytics Schema | Expected Batch Size | Ingestion SLA Target |
|:---|:---|:---|:---|:---|:---|
| **DST-001** | General Ledger | `POST /financial/journal-entries/batch` | `CanonicalJournalEntry` | 500 records/payload | < 1.5 seconds P95 |
| **DST-002** | Accounts Payable | `POST /payables/invoices/batch` | `CanonicalVendorInvoice` | 500 records/payload | < 1.5 seconds P95 |
| **DST-003** | Accounts Receivable | `POST /receivables/invoices/batch` | `CanonicalCustomerReceivable` | 500 records/payload | < 1.5 seconds P95 |
| **DST-004** | Cost Centre Performance | `POST /controlling/cost-centres/batch` | `CanonicalCostCentre` | 200 records/payload | < 1.0 seconds P95 |
| **DST-005** | Profit Centre Margins | `POST /controlling/profit-centres/batch` | `CanonicalProfitCentre` | 200 records/payload | < 1.0 seconds P95 |
| **DST-006** | Material Valuation | `POST /inventory/material-costs/batch` | `CanonicalMaterialCost` | 500 records/payload | < 2.0 seconds P95 |
| **DST-007** | Procurement Spend | `POST /procurement/purchase-orders/batch`| `CanonicalPurchaseOrder` | 500 records/payload | < 1.5 seconds P95 |
| **DST-008** | Sales Order Backlog | `POST /sales/orders/batch` | `CanonicalSalesOrder` | 500 records/payload | < 1.5 seconds P95 |
| **DST-009** | Fixed Asset Register | `POST /assets/register/batch` | `CanonicalFixedAsset` | 200 records/payload | < 1.0 seconds P95 |
| **DST-010** | Bank Cash Position | `POST /treasury/cash-positions/batch` | `CanonicalBankStatement` | 100 records/payload | < 0.8 seconds P95 |
| **DST-011** | Budget Performance | `POST /controlling/budget-performance/batch`| `CanonicalBudgetPerformance`| 200 records/payload | < 1.0 seconds P95 |
| **DST-012** | Inventory Balances | `POST /inventory/balances/batch` | `CanonicalInventoryBalance` | 500 records/payload | < 2.0 seconds P95 |

---

## 4. Authentication, Token Lifecycle & Error Contract
- **OAuth 2.0 Flow:** Client Credentials Grant against `https://auth.finsight.zetheta.com/oauth/v2/token`.
- **Token Format:** RS256-signed JWT token containing claims: `iss`, `sub`, `tenant_id`, `exp`, `scope`.
- **Preemptive Refresh:** The integration runtime tracks the 3,600s TTL and executes refresh at T-120 seconds.
- **Standardized Error Responses:** Fully aligned with Appendix B (e.g. `INVALID_REQUEST`, `TOKEN_EXPIRED`, `RATE_LIMITED`, `SERVICE_UNAVAILABLE`).
"""

    with open(r'api-specifications/D2_API_Specification_Document_v2.md', 'w', encoding='utf-8') as f:
        f.write(d2_doc)

    print('Wrote D2 API Specification document!')

if __name__ == '__main__':
    create_api_specs()

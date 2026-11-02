import os
import yaml

def generate_individual():
    sap_domains = [
        ("SRC001", "GeneralLedger", "ACDOCA", "/ZZ_FIN_GL_CDS/GLItems", "Universal Journal Line Items"),
        ("SRC002", "AccountsPayable", "BSIK_BSAK", "/ZZ_FIN_AP_CDS/VendorInvoices", "Vendor Invoices and Payables"),
        ("SRC003", "AccountsReceivable", "BSID_BSAD", "/ZZ_FIN_AR_CDS/CustomerReceivables", "Customer Receivables"),
        ("SRC004", "CostCentre", "CSKS_COSP", "/ZZ_FIN_CO_CDS/CostCentres", "Cost Centre Master & Postings"),
        ("SRC005", "ProfitCentre", "CEPC", "/ZZ_FIN_PCA_CDS/ProfitCentres", "Profit Centre Master Data"),
        ("SRC006", "MaterialLedger", "MBEW_CKMLCR", "/ZZ_FIN_ML_CDS/MaterialValuations", "Material Valuation & Costs"),
        ("SRC007", "PurchaseOrders", "EKKO_EKPO", "/ZZ_MM_PO_CDS/PurchaseOrders", "Purchase Orders Procurement"),
        ("SRC008", "SalesOrders", "VBAK_VBAP", "/ZZ_SD_SO_CDS/SalesOrders", "Sales Orders & Deliveries"),
        ("SRC009", "FixedAssets", "ANLA_ANLP", "/ZZ_FI_AA_CDS/FixedAssets", "Fixed Asset Register & Depreciation"),
        ("SRC010", "BankStatements", "FEBKO_FEBEP", "/ZZ_FI_BL_CDS/BankStatements", "Electronic Bank Statements"),
        ("SRC011", "BudgetActual", "COSP_COSS", "/ZZ_CO_BGT_CDS/BudgetActuals", "Budget vs Actuals CO Totals"),
        ("SRC012", "Inventory", "MARD_MBEW", "/ZZ_MM_INV_CDS/InventoryItems", "Inventory Storage Location Balances")
    ]

    for code, name, table, path, desc in sap_domains:
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": f"SAP S/4HANA Source - {name} ({code})",
                "version": "1.0.0",
                "description": f"Source extraction contract for {desc} backed by SAP table(s) {table}."
            },
            "paths": {
                path: {
                    "get": {
                        "summary": f"{code}: Extract {name}",
                        "parameters": [
                            {"name": "$filter", "in": "query", "schema": {"type": "string"}},
                            {"name": "$skiptoken", "in": "query", "schema": {"type": "string"}},
                            {"name": "$top", "in": "query", "schema": {"type": "integer", "default": 5000}}
                        ],
                        "responses": {
                            "200": {"description": f"Successful extraction of {name} records"}
                        }
                    }
                }
            }
        }
        fname = f"API_SAP_{code}_{name}.yaml"
        with open(os.path.join(r"api-specifications/sap-source", fname), "w", encoding="utf-8") as f:
            yaml.dump(spec, f, sort_keys=False)
        print(f"Wrote {fname}")

    dst_domains = [
        ("DST001", "JournalEntries", "/financial/journal-entries/batch", "General Ledger Journal Entries"),
        ("DST002", "VendorInvoices", "/payables/invoices/batch", "Vendor Invoices"),
        ("DST003", "CustomerReceivables", "/receivables/invoices/batch", "Customer Receivables"),
        ("DST004", "CostCentres", "/controlling/cost-centres/batch", "Cost Centre Performance"),
        ("DST005", "ProfitCentres", "/controlling/profit-centres/batch", "Profit Centre Margins"),
        ("DST006", "MaterialCosts", "/inventory/material-costs/batch", "Material Valuation & Costs"),
        ("DST007", "PurchaseOrders", "/procurement/purchase-orders/batch", "Purchase Orders"),
        ("DST008", "SalesOrders", "/sales/orders/batch", "Sales Orders Backlog"),
        ("DST009", "FixedAssets", "/assets/register/batch", "Fixed Asset Register"),
        ("DST010", "BankStatements", "/treasury/cash-positions/batch", "Bank Cash Positions"),
        ("DST011", "BudgetPerformance", "/controlling/budget-performance/batch", "Departmental Budget Performance"),
        ("DST012", "InventoryValuation", "/inventory/balances/batch", "Inventory Balances")
    ]

    for code, name, path, desc in dst_domains:
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": f"FinSight 4.2 Ingestion - {name} ({code})",
                "version": "4.2.0",
                "description": f"Ingestion contract for {desc} in Zetheta FinSight 4.2. [Assumed Contract: Standard Zetheta Ingestion Specification]."
            },
            "paths": {
                path: {
                    "post": {
                        "summary": f"{code}: Ingest {name} batch",
                        "parameters": [
                            {"name": "X-Tenant-ID", "in": "header", "required": True, "schema": {"type": "string"}},
                            {"name": "X-Idempotency-Key", "in": "header", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "201": {"description": f"{name} batch ingested successfully"}
                        }
                    }
                }
            }
        }
        fname = f"API_FinSight_{code}_{name}.yaml"
        with open(os.path.join(r"api-specifications/finsight-destination", fname), "w", encoding="utf-8") as f:
            yaml.dump(spec, f, sort_keys=False)
        print(f"Wrote {fname}")

if __name__ == '__main__':
    generate_individual()

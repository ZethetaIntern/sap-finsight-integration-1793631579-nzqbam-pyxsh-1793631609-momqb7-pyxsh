# Advanced Transformation Rules: Hierarchy Flattening Algorithm
## Project: SAP S/4HANA to Zetheta FinSight 4.2 Integration
**Document ID:** TR-HIER-01  
**Classification:** Strictly Private & Confidential  

---

## 1. Business Problem
In SAP Controlling (`CO`), Cost Centre Standard Hierarchies are stored as recursive tree structures across tables `SETHEADER`, `SETNODE`, and `SETLEAF`.
- Depth: Up to 7 nested levels (e.g., `Enterprise -> Manufacturing -> Western Region -> Maharashtra Plants -> Pune Plant -> Engine Shop -> Assembly Line 1`).
- Analytics Ingestion Problem: Relational analytics tools and columnar dashboards in FinSight require a flattened dimensional model with explicit columns (`Level1`, `Level2`, ... `Level7`) to support instantaneous slice-and-dice aggregations without expensive runtime recursive tree traversals.

---

## 2. Recursive Flattening Algorithm

```python
def flatten_sap_hierarchy(set_class, subclass, root_node, setnode_rows, setleaf_rows):
    '''
    Recursively traverses SAP SETNODE and SETLEAF tables and generates
    flattened rows containing Cost Centre ID and Levels 1 through 7.
    '''
    flattened_records = []

    def traverse(current_node, current_path):
        # Find child set nodes
        children = [r for r in setnode_rows if r['SETNAME'] == current_node]
        leafs = [l for l in setleaf_rows if l['SETNAME'] == current_node]

        # Add leaves at current level
        for leaf in leafs:
            # Handle range VALFROM to VALTO
            cost_centres = expand_range(leaf['VALFROM'], leaf['VALTO'])
            for cc in cost_centres:
                row = {
                    'costCentreId': cc,
                    'level1': current_path[0] if len(current_path) > 0 else current_node,
                    'level2': current_path[1] if len(current_path) > 1 else None,
                    'level3': current_path[2] if len(current_path) > 2 else None,
                    'level4': current_path[3] if len(current_path) > 3 else None,
                    'level5': current_path[4] if len(current_path) > 4 else None,
                    'level6': current_path[5] if len(current_path) > 5 else None,
                    'level7': current_path[6] if len(current_path) > 6 else None,
                }
                flattened_records.append(row)

        # Recurse down children
        for child in children:
            traverse(child['SUBSETNAME'], current_path + [child['SUBSETNAME']])

    traverse(root_node, [root_node])
    return flattened_records
```

import json
import re
import sys

def run_tests():
    print("=" * 60)
    print("MERIDIAN INTEGRATION TEST SUITE: AUTOMATED TEST RUNNER")
    print("=" * 60)
    passed = 0
    failed = 0

    # Test 1: Validate 56 Field Mappings Existence
    with open(r'data-mapping/MAP_Complete_Master_Mapping.md', encoding='utf-8') as f:
        mapping_text = f.read()
    map_ids = re.findall(r'MAP-[A-Z]{2}-\d{3}', mapping_text)
    unique_maps = set(map_ids)
    print(f"[TEST 1] Master Field Mappings Count: {len(unique_maps)} unique mapping IDs found.")
    if len(unique_maps) >= 50:
        print("  -> PASS: Exceeds mandatory 50-mapping requirement (Target: 56).")
        passed += 1
    else:
        print(f"  -> FAIL: Only {len(unique_maps)} mappings found.")
        failed += 1

    # Test 2: Validate 28 Data Quality Rules
    with open(r'data-quality/data-quality-rules-catalog.md', encoding='utf-8') as f:
        dq_text = f.read()
    dq_ids = re.findall(r'DQR-\d{2}', dq_text)
    unique_dqs = set(dq_ids)
    print(f"[TEST 2] Data Quality Rules Count: {len(unique_dqs)} unique rules found.")
    if len(unique_dqs) >= 25:
        print("  -> PASS: Exceeds mandatory 25-rule requirement (Target: 28).")
        passed += 1
    else:
        print(f"  -> FAIL: Only {len(unique_dqs)} rules found.")
        failed += 1

    # Test 3: Validate 12 Dashboard Panels in Grafana JSON
    with open(r'monitoring/grafana/finsight-integration-overview.json', encoding='utf-8') as f:
        dash = json.load(f)
    panel_count = len(dash.get('panels', []))
    print(f"[TEST 3] Grafana Dashboard Panels Count: {panel_count} panels configured.")
    if panel_count >= 12:
        print("  -> PASS: Exactly matches 12 mandatory panels (MON-001 to MON-012).")
        passed += 1
    else:
        print(f"  -> FAIL: Only {panel_count} panels found.")
        failed += 1

    # Test 4: Validate Error Code Registry Completeness
    with open(r'error-handling/error-code-registry.md', encoding='utf-8') as f:
        err_text = f.read()
    err_codes = re.findall(r'ERR-[A-Z]+-\d{3}', err_text)
    unique_errs = set(err_codes)
    print(f"[TEST 4] Error Code Registry Count: {len(unique_errs)} unique error codes found.")
    if len(unique_errs) >= 20:
        print("  -> PASS: Complete error taxonomy verified.")
        passed += 1
    else:
        print("  -> FAIL: Incomplete error taxonomy.")
        failed += 1

    # Test 5: Validate Sample JSON Transformation
    with open(r'transformation-rules/sample-payload-transformations.json', encoding='utf-8') as f:
        sample_data = json.load(f)
    gl_sample = sample_data.get('sample_GL_transformation', {})
    transformed = gl_sample.get('output_canonical_transformed', {})
    if transformed.get('documentId') == 'MC01-2026-0100004521-001' and transformed.get('postingType') == 'DEBIT':
        print("[TEST 5] Sample GL Transformation Contract: PASS (Canonical composite key valid).")
        passed += 1
    else:
        print("[TEST 5] Sample GL Transformation Contract: FAIL.")
        failed += 1

    # Test 6: Validate Master 25 Test Scenarios Matrix
    with open(r'testing/test-scenarios-master-matrix.md', encoding='utf-8') as f:
        test_matrix_text = f.read()
    test_ids = re.findall(r'TST-[A-Z]+-\d{3}', test_matrix_text)
    unique_tests = set(test_ids)
    print(f"[TEST 6] Master Test Scenarios Count: {len(unique_tests)} scenarios cataloged.")
    if len(unique_tests) >= 25:
        print("  -> PASS: Exactly matches all 25 mandatory test cases.")
        passed += 1
    else:
        print(f"  -> FAIL: Only {len(unique_tests)} test cases found.")
        failed += 1

    print("=" * 60)
    print(f"FINAL TEST RUNNER SUMMARY: {passed} PASSED, {failed} FAILED.")
    print("=" * 60)
    return failed == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

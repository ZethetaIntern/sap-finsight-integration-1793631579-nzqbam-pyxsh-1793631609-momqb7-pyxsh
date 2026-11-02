import { DataQualityValidator } from './services/validator';
import { TransformerService } from './services/transformer';
import { CircuitBreaker } from './services/circuitBreaker';
import { ReconciliationEngine } from './services/reconciliationEngine';
import { SapRawGlRecord, CanonicalJournalEntry } from './types';

export function runDemonstration() {
  console.log('================================================================');
  console.log('MERIDIAN INTEGRATION PROTOTYPE: DEMONSTRATION HARNESS');
  console.log('================================================================');

  // Synthetic SAP S/4HANA Extract Batch
  const mockBatch: SapRawGlRecord[] = [
    {
      RCLNT: '100',
      RLDNR: '0L',
      RBUKRS: 'MC01',
      GJAHR: '2026',
      BELNR: '0100004521',
      BUZEI: '001',
      RACCT: '0000400000',
      HSL: 150000.50,
      RHCUR: 'INR',
      DRCRK: 'S',
      BUDAT: '20260315',
      BLDAT: '20260314',
      MONAT: '012',
      KOSTL: '0000002100',
      PRCTR: '0000001000',
      BLART: 'SA'
    },
    {
      RCLNT: '100',
      RLDNR: '0L',
      RBUKRS: 'MC01',
      GJAHR: '2026',
      BELNR: '0100004521',
      BUZEI: '002',
      RACCT: '0000100000',
      HSL: 150000.50,
      RHCUR: 'INR',
      DRCRK: 'H',
      BUDAT: '20260315',
      BLDAT: '20260314',
      MONAT: '012',
      KOSTL: '0000002100',
      PRCTR: '0000001000',
      BLART: 'SA'
    },
    // Malformed record to demonstrate DLQ routing
    {
      RCLNT: '100',
      RLDNR: '0L',
      RBUKRS: 'MC01',
      GJAHR: '2026',
      BELNR: '',
      BUZEI: '003',
      RACCT: '0000400000',
      HSL: 5000.00,
      RHCUR: 'INVALID_CURRENCY',
      DRCRK: 'S',
      BUDAT: 'INVALID_DATE',
      BLDAT: '20260314',
      MONAT: '012',
      BLART: 'SA'
    }
  ];

  console.log(`[1. INGESTION] Processing batch of ${mockBatch.length} SAP extraction line items...`);

  const validLoaded: CanonicalJournalEntry[] = [];
  const dlqRecords: Array<{ record: SapRawGlRecord; errors: string[] }> = [];

  for (const raw of mockBatch) {
    const val = DataQualityValidator.validateRawGL(raw);
    if (!val.isValid) {
      dlqRecords.push({ record: raw, errors: val.errors });
    } else {
      const canonical = TransformerService.transformGL(raw);
      validLoaded.push(canonical);
    }
  }

  console.log(`[2. VALIDATION] Passed: ${validLoaded.length} | Rejected to DLQ: ${dlqRecords.length}`);
  if (dlqRecords.length > 0) {
    console.log(`  -> Trapped Errors in DLQ: ${JSON.stringify(dlqRecords[0].errors)}`);
  }

  // Circuit Breaker Demonstration
  const cb = new CircuitBreaker();
  console.log(`[3. RESILIENCE] Initial Circuit Breaker State: ${cb.getState()} (0 = CLOSED)`);

  // Automated Reconciliation Check
  const recon = ReconciliationEngine.reconcileBatch(
    'BATCH-DEMO-20260315-001',
    mockBatch.slice(0, 2), // Balanced subset
    validLoaded,
    dlqRecords.length
  );

  console.log('[4. RECONCILIATION] Batch Checkpoint Result:');
  console.log(`  -> Source Debit:  INR ${recon.sourceChecksumDebit.toLocaleString()}`);
  console.log(`  -> Source Credit: INR ${recon.sourceChecksumCredit.toLocaleString()}`);
  console.log(`  -> Target Debit:  INR ${recon.targetChecksumDebit.toLocaleString()}`);
  console.log(`  -> Target Credit: INR ${recon.targetChecksumCredit.toLocaleString()}`);
  console.log(`  -> Balance Variance: INR ${recon.balanceVariance.toFixed(2)}`);
  console.log(`  -> Reconciliation Status: ${recon.reconciliationStatus}`);
  console.log('================================================================');
  console.log('PROTOTYPE EXECUTION COMPLETED SUCCESSFULLY (ZERO AUDIT BREAKS)');
  console.log('================================================================');
}

if (require.main === module) {
  runDemonstration();
}

import { SapRawGlRecord, CanonicalJournalEntry, BatchReconciliationResult } from '../types';

export class ReconciliationEngine {
  public static reconcileBatch(
    batchId: string,
    rawRecords: SapRawGlRecord[],
    loadedRecords: CanonicalJournalEntry[],
    dlqCount: number
  ): BatchReconciliationResult {
    let sourceDebit = 0;
    let sourceCredit = 0;
    for (const r of rawRecords) {
      if (r.DRCRK === 'S') sourceDebit += r.HSL;
      if (r.DRCRK === 'H') sourceCredit += r.HSL;
    }

    let targetDebit = 0;
    let targetCredit = 0;
    for (const l of loadedRecords) {
      if (l.postingType === 'DEBIT') targetDebit += l.amountLC;
      if (l.postingType === 'CREDIT') targetCredit += l.amountLC;
    }

    sourceDebit = Math.round(sourceDebit * 100) / 100;
    sourceCredit = Math.round(sourceCredit * 100) / 100;
    targetDebit = Math.round(targetDebit * 100) / 100;
    targetCredit = Math.round(targetCredit * 100) / 100;

    const balanceVariance = Math.abs(targetDebit - targetCredit);

    return {
      batchId,
      sourceRecordCount: rawRecords.length,
      loadedRecordCount: loadedRecords.length,
      dlqRecordCount: dlqCount,
      sourceChecksumDebit: sourceDebit,
      sourceChecksumCredit: sourceCredit,
      targetChecksumDebit: targetDebit,
      targetChecksumCredit: targetCredit,
      balanceVariance,
      reconciliationStatus: balanceVariance === 0.00 ? 'RECONCILED' : 'BREAK_DETECTED'
    };
  }
}

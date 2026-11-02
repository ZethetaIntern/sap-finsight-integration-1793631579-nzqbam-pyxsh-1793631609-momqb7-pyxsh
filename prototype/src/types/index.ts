export interface SapRawGlRecord {
  RCLNT: string;
  RLDNR: string;
  RBUKRS: string;
  GJAHR: string;
  BELNR: string;
  BUZEI: string;
  RACCT: string;
  HSL: number;
  RHCUR: string;
  WSL?: number;
  RWCUR?: string;
  DRCRK: 'S' | 'H';
  BUDAT: string;
  BLDAT: string;
  MONAT: string;
  KOSTL?: string;
  PRCTR?: string;
  BLART: string;
}

export interface CanonicalJournalEntry {
  documentId: string;
  companyCode: string;
  fiscalYear: number;
  documentNumber: string;
  lineItem: number;
  postingDate: string;
  documentDate: string;
  glAccount: string;
  amountLC: number;
  localCurrency: string;
  amountTC?: number;
  transactionCurrency?: string;
  postingType: 'DEBIT' | 'CREDIT';
  costCentre: string | null;
  profitCentre: string | null;
  fiscalPeriod: string;
  isSpecialPeriod: boolean;
  documentType: string;
  isReversal: boolean;
}

export interface BatchReconciliationResult {
  batchId: string;
  sourceRecordCount: number;
  loadedRecordCount: number;
  dlqRecordCount: number;
  sourceChecksumDebit: number;
  sourceChecksumCredit: number;
  targetChecksumDebit: number;
  targetChecksumCredit: number;
  balanceVariance: number;
  reconciliationStatus: 'RECONCILED' | 'BREAK_DETECTED';
}

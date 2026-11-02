import { SapRawGlRecord, CanonicalJournalEntry } from '../types';

export class TransformerService {
  public static transformGL(raw: SapRawGlRecord): CanonicalJournalEntry {
    const cleanBelnr = raw.BELNR.replace(/^0+/, '');
    const cleanRacct = raw.RACCT.replace(/^0+/, '');
    const cleanKostl = raw.KOSTL ? raw.KOSTL.replace(/^0+/, '') : null;
    const cleanPrctr = raw.PRCTR ? raw.PRCTR.replace(/^0+/, '') : null;

    // Format YYYYMMDD to YYYY-MM-DD
    const postingDate = `${raw.BUDAT.substring(0, 4)}-${raw.BUDAT.substring(4, 6)}-${raw.BUDAT.substring(6, 8)}`;
    const documentDate = `${raw.BLDAT.substring(0, 4)}-${raw.BLDAT.substring(4, 6)}-${raw.BLDAT.substring(6, 8)}`;

    // Fiscal period mapping (Variant V3 April-March)
    const periodNum = parseInt(raw.MONAT, 10);
    const gjahr = parseInt(raw.GJAHR, 10);
    let fiscalPeriod = '';
    let isSpecialPeriod = false;

    if (periodNum >= 1 && periodNum <= 9) {
      fiscalPeriod = `${gjahr}-${String(periodNum + 3).padStart(2, '0')}`;
    } else if (periodNum >= 10 && periodNum <= 12) {
      fiscalPeriod = `${gjahr + 1}-${String(periodNum - 9).padStart(2, '0')}`;
    } else {
      fiscalPeriod = `${gjahr + 1}-03`;
      isSpecialPeriod = true;
    }

    return {
      documentId: `${raw.RBUKRS}-${raw.GJAHR}-${cleanBelnr}-${raw.BUZEI}`,
      companyCode: raw.RBUKRS,
      fiscalYear: gjahr,
      documentNumber: cleanBelnr,
      lineItem: parseInt(raw.BUZEI, 10),
      postingDate,
      documentDate,
      glAccount: cleanRacct,
      amountLC: Math.abs(raw.HSL),
      localCurrency: raw.RHCUR.toUpperCase(),
      amountTC: raw.WSL ? Math.abs(raw.WSL) : undefined,
      transactionCurrency: raw.RWCUR ? raw.RWCUR.toUpperCase() : undefined,
      postingType: raw.DRCRK === 'S' ? 'DEBIT' : 'CREDIT',
      costCentre: cleanKostl,
      profitCentre: cleanPrctr,
      fiscalPeriod,
      isSpecialPeriod,
      documentType: raw.BLART === 'SA' ? 'GL_ACCOUNT_POSTING' : raw.BLART,
      isReversal: false
    };
  }
}

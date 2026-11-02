import { SapRawGlRecord } from '../types';

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export class DataQualityValidator {
  public static validateRawGL(record: SapRawGlRecord): ValidationResult {
    const errors: string[] = [];

    // DQR-01 & DQR-02: Null checks
    if (!record.RBUKRS) errors.push('ERR-MAP-001: Company code RBUKRS is null');
    if (!record.BELNR) errors.push('ERR-MAP-001: Document number BELNR is null');
    if (!record.GJAHR) errors.push('ERR-MAP-001: Fiscal year GJAHR is null');
    if (!record.RACCT) errors.push('ERR-MAP-001: GL Account RACCT is null');

    // DQR-06: Date format (YYYYMMDD)
    if (!/^\d{8}$/.test(record.BUDAT)) {
      errors.push(`ERR-MAP-002: Invalid posting date format BUDAT: ${record.BUDAT}`);
    }

    // DQR-14: Future posting date check
    const currentYear = new Date().getFullYear();
    const docYear = parseInt(record.BUDAT.substring(0, 4), 10);
    if (docYear > currentYear + 1) {
      errors.push(`ERR-VAL-007: Posting date too far in future: ${record.BUDAT}`);
    }

    // DQR-11: Numerical range checks
    if (typeof record.HSL !== 'number' || isNaN(record.HSL)) {
      errors.push('ERR-MAP-006: Amount HSL is not a valid number');
    }

    // DQR-07: Currency check
    if (!record.RHCUR || record.RHCUR.length !== 3) {
      errors.push(`ERR-MAP-004: Invalid currency code: ${record.RHCUR}`);
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

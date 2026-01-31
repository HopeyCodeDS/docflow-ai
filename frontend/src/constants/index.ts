/** App-wide constants and helpers. */

export const RAW_TEXT_PREVIEW_LENGTH = 500;
export const EXTRACTION_REFRESH_DELAY_MS = 2000;

/** All document statuses for filter dropdown (order matches typical workflow). */
export const DOCUMENT_STATUSES = [
  'UPLOADED',
  'PROCESSING',
  'EXTRACTED',
  'VALIDATED',
  'REVIEWED',
  'EXPORTED',
  'FAILED',
] as const;

export const DOCUMENT_STATUS_BADGES: Record<string, string> = {
  UPLOADED: 'badge-info',
  PROCESSING: 'badge-warning',
  EXTRACTED: 'badge-success',
  VALIDATED: 'badge-success',
  REVIEWED: 'badge-success',
  EXPORTED: 'badge-success',
  FAILED: 'badge-danger',
};

export function getStatusBadge(status: string): string {
  return DOCUMENT_STATUS_BADGES[status] ?? 'badge-secondary';
}

export type ConfidenceLevel = 'high' | 'medium' | 'low';

export function getConfidenceClass(confidence: number): ConfidenceLevel {
  if (confidence >= 0.7) return 'high';
  if (confidence >= 0.4) return 'medium';
  return 'low';
}

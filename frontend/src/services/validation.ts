import client from '../api/client';

export interface ValidationErrorItem {
  field: string;
  message: string;
  severity: string;
}

export interface ValidationResult {
  validation_status: string;
  validation_errors: ValidationErrorItem[];
}

export function getValidation(documentId: string): Promise<ValidationResult> {
  return client.get<ValidationResult>(`/documents/${documentId}/validation`).then((r) => r.data);
}

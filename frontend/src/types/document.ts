/** Shared types aligned with backend DTOs. Re-export from services where defined. */
export type { Document, DocumentListResponse } from '../services/documents';
export type { Extraction } from '../services/extractions';
export type { ValidationResult, ValidationErrorItem } from '../services/validation';
export type { Review, ReviewCreate } from '../services/reviews';

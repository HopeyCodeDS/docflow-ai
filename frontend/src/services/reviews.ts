import client from '../api/client';

export interface ReviewCreate {
  corrections: Record<string, string>;
  review_notes?: string;
}

export interface Review {
  id: string;
  document_id: string;
  reviewed_by: string;
  corrections: Record<string, string>;
  review_status: string;
  review_notes: string | null;
  reviewed_at: string;
}

export function getReview(documentId: string): Promise<Review> {
  return client.get<Review>(`/documents/${documentId}/review`).then((r) => r.data);
}

export function createReview(documentId: string, data: ReviewCreate): Promise<Review> {
  return client.post<Review>(`/documents/${documentId}/review`, data).then((r) => r.data);
}

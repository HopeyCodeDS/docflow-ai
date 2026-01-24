import client from '../api/client';

export interface Document {
  id: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  uploaded_at: string;
  uploaded_by: string;
  status: string;
  document_type: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
}

export function getDocuments(params?: { skip?: number; limit?: number; status?: string }): Promise<DocumentListResponse> {
  return client.get<DocumentListResponse>('/documents', { params }).then((r) => r.data);
}

export function uploadDocument(file: File): Promise<Document> {
  const form = new FormData();
  form.append('file', file);
  return client.post<Document>('/documents', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
}

export function getDocument(id: string): Promise<Document> {
  return client.get<Document>(`/documents/${id}`).then((r) => r.data);
}

export function deleteDocument(id: string): Promise<{ message: string }> {
  return client.delete<{ message: string }>(`/documents/${id}`).then((r) => r.data);
}

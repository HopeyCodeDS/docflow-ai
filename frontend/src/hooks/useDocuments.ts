import { useState, useEffect, useCallback } from 'react';
import * as documentsService from '../services/documents';

export interface DocumentFilters {
  status?: string;
  filename?: string;
  date_from?: string;
  date_to?: string;
}

export function useDocuments(params?: { limit?: number; filters?: DocumentFilters }) {
  const [documents, setDocuments] = useState<documentsService.Document[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await documentsService.getDocuments({
        limit: params?.limit ?? 50,
        skip: 0,
        ...params?.filters,
      });
      setDocuments(res.documents);
      setTotal(res.total);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [params?.limit, params?.filters?.status, params?.filters?.filename, params?.filters?.date_from, params?.filters?.date_to]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const deleteDocument = useCallback(async (id: string) => {
    await documentsService.deleteDocument(id);
    await refresh();
  }, [refresh]);

  return { documents, total, loading, error, refresh, deleteDocument };
}

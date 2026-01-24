import { useState, useEffect, useCallback } from 'react';
import * as documentsService from '../services/documents';

export function useDocuments(params?: { limit?: number }) {
  const [documents, setDocuments] = useState<documentsService.Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await documentsService.getDocuments({ limit: params?.limit ?? 50 });
      setDocuments(res.documents);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [params?.limit]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const deleteDocument = useCallback(async (id: string) => {
    await documentsService.deleteDocument(id);
    await refresh();
  }, [refresh]);

  return { documents, loading, error, refresh, deleteDocument };
}

import { useState, useEffect, useCallback } from 'react';
import * as extractionsService from '../services/extractions';
import * as validationService from '../services/validation';
import * as reviewsService from '../services/reviews';
import { EXTRACTION_REFRESH_DELAY_MS } from '../constants';

export function useDocumentReview(documentId: string | undefined) {
  const [extraction, setExtraction] = useState<extractionsService.Extraction | null>(null);
  const [validation, setValidation] = useState<validationService.ValidationResult | null>(null);
  const [corrections, setCorrections] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    try {
      const ext = await extractionsService.getExtraction(documentId).catch(() => null);
      if (ext) {
        setExtraction(ext);
        setCorrections((ext.structured_data as Record<string, string>) || {});
        const hasStructured = ext.structured_data && Object.keys(ext.structured_data).length > 0;
        if (hasStructured) {
          validationService.getValidation(documentId).then((v) => setValidation(v)).catch(() => {});
        }
      } else {
        setExtraction(null);
      }
    } catch {
      setExtraction(null);
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const setCorrection = useCallback((field: string, value: string) => {
    setCorrections((prev) => ({ ...prev, [field]: value }));
  }, []);

  const save = useCallback(async () => {
    if (!documentId) return;
    setSaving(true);
    try {
      await reviewsService.createReview(documentId, { corrections, review_notes: '' });
      return true;
    } finally {
      setSaving(false);
    }
  }, [documentId, corrections]);

  const retryExtraction = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    try {
      await extractionsService.retryExtraction(documentId);
      setTimeout(fetchData, EXTRACTION_REFRESH_DELAY_MS);
    } catch {
      setLoading(false);
    }
  }, [documentId, fetchData]);

  return {
    extraction,
    validation,
    corrections,
    setCorrection,
    save,
    retryExtraction,
    fetchData,
    loading,
    saving,
  };
}

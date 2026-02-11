import { useState, useEffect, useCallback, useMemo } from 'react';
import * as extractionsService from '../services/extractions';
import * as validationService from '../services/validation';
import * as reviewsService from '../services/reviews';
import { EXTRACTION_REFRESH_DELAY_MS } from '../constants';

const REVIEW_STATUSES = new Set(['REVIEWED', 'EXPORTED']);

export function useDocumentReview(documentId: string | undefined, documentStatus?: string | null) {
  const [extraction, setExtraction] = useState<extractionsService.Extraction | null>(null);
  const [validation, setValidation] = useState<validationService.ValidationResult | null>(null);
  const [review, setReview] = useState<reviewsService.Review | null>(null);
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

  // Fetch existing review if document is REVIEWED or beyond
  const fetchReview = useCallback(async () => {
    if (!documentId) return;
    try {
      const r = await reviewsService.getReview(documentId);
      setReview(r);
      // Pre-fill corrections from review if it exists
      if (r.corrections && Object.keys(r.corrections).length > 0) {
        setCorrections(r.corrections);
      }
    } catch {
      setReview(null);
    }
  }, [documentId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (documentStatus && REVIEW_STATUSES.has(documentStatus)) {
      fetchReview();
    }
  }, [documentStatus, fetchReview]);

  const setCorrection = useCallback((field: string, value: string) => {
    setCorrections((prev) => ({ ...prev, [field]: value }));
  }, []);

  const save = useCallback(async () => {
    if (!documentId) return;
    setSaving(true);
    try {
      const r = await reviewsService.createReview(documentId, { corrections, review_notes: '' });
      setReview(r);
      return true;
    } finally {
      setSaving(false);
    }
  }, [documentId, corrections]);

  const approve = useCallback(async () => {
    if (!documentId) return;
    const r = await reviewsService.approveReview(documentId);
    setReview(r);
  }, [documentId]);

  const reject = useCallback(async () => {
    if (!documentId) return;
    const r = await reviewsService.rejectReview(documentId);
    setReview(r);
  }, [documentId]);

  const retryExtraction = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    try {
      await extractionsService.retryExtraction(documentId);
      setReview(null);
      setValidation(null);
      setTimeout(fetchData, EXTRACTION_REFRESH_DELAY_MS);
    } catch {
      setLoading(false);
    }
  }, [documentId, fetchData]);

  const canSave = useMemo(() => {
    if (!validation) return true; // No validation yet — backend will gate
    return validation.validation_status !== 'FAILED';
  }, [validation]);

  return {
    extraction,
    validation,
    review,
    corrections,
    setCorrection,
    save,
    approve,
    reject,
    retryExtraction,
    fetchData,
    fetchReview,
    loading,
    saving,
    canSave,
  };
}

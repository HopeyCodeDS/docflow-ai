import React, { useCallback, Fragment, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocumentReview } from '../hooks/useDocumentReview';
import { getDocument } from '../services/documents';
import client from '../api/client';
import { getConfidenceClass, RAW_TEXT_PREVIEW_LENGTH } from '../constants';
import './DocumentReview.css';

const DocumentReview: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const {
    extraction,
    validation,
    corrections,
    setCorrection,
    save,
    retryExtraction,
    fetchData,
    loading,
    saving,
  } = useDocumentReview(documentId);
  const [documentStatus, setDocumentStatus] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [restartingProcessing, setRestartingProcessing] = useState(false);

  const refreshDocumentStatus = useCallback(async () => {
    if (!documentId) return;
    try {
      const d = await getDocument(documentId);
      setDocumentStatus(d.status);
    } catch {
      // ignore
    }
  }, [documentId]);

  const refreshData = useCallback(async () => {
    setRefreshing(true);
    try {
      await fetchData();
      await refreshDocumentStatus();
    } finally {
      setRefreshing(false);
    }
  }, [fetchData, refreshDocumentStatus]);

  useEffect(() => {
    refreshDocumentStatus();
  }, [refreshDocumentStatus]);

  useEffect(() => {
    if (documentStatus !== 'PROCESSING') return;
    const t = setInterval(refreshData, 5000);
    return () => clearInterval(t);
  }, [documentStatus, refreshData]);

  const handleRestartProcessing = useCallback(async () => {
    if (!documentId) return;
    setRestartingProcessing(true);
    try {
      await client.post(`/documents/${documentId}/reprocess`);
      await refreshData();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to restart processing');
    } finally {
      setRestartingProcessing(false);
    }
  }, [documentId, refreshData]);

  const handleSave = async () => {
    try {
      await save();
      navigate('/dashboard');
    } catch (e) {
      alert((e as Error).message || 'Failed to save review');
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  const isProcessing = documentStatus === 'PROCESSING';
  const pipelineStages: readonly string[] = ['UPLOADED', 'PROCESSING', 'EXTRACTED', 'VALIDATED', 'REVIEWED', 'EXPORTED', 'FAILED'];
  const currentStageIndex = documentStatus ? pipelineStages.indexOf(documentStatus) : 0;

  const pipelineStrip = (
    <div className="pipeline-strip" role="status" aria-label={`Processing stage: ${documentStatus ?? 'unknown'}`}>
      {pipelineStages.map((stage, i) => (
        <Fragment key={stage}>
          <span
            className={`pipeline-step ${i <= currentStageIndex ? 'done' : ''} ${documentStatus === stage ? 'current' : ''} ${stage === 'FAILED' ? 'step-failed' : ''}`}
          >
            {stage.charAt(0) + stage.slice(1).toLowerCase().replace(/_/g, ' ')}
          </span>
          {i < pipelineStages.length - 1 && <span className="pipeline-connector" aria-hidden />}
        </Fragment>
      ))}
    </div>
  );

  const reviewHeader = (
    <div className="card-header-row">
      <h2>Review Document</h2>
      <button
        type="button"
        className="btn-refresh"
        onClick={refreshData}
        disabled={refreshing}
        title="Refresh status"
        aria-label="Refresh status"
      >
        <svg
          className={refreshing ? 'spin' : ''}
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M23 4v6h-6" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
      </button>
    </div>
  );

  if (!extraction) {
    return (
      <div className="container">
        <div className="card">
          {reviewHeader}
          {pipelineStrip}
          {isProcessing && (
            <div className="processing-banner" role="status">
              <span className="processing-banner-text">Processing in progress.</span>
              <span> Use the refresh button to see the latest status.</span>
            </div>
          )}
          <p>Extraction not found. The document may still be processing.</p>
          <div style={{ marginTop: '20px' }}>
            <button onClick={retryExtraction} className="btn btn-primary" disabled={loading}>
              {loading ? 'Processing...' : 'Start Extraction'}
            </button>
            <button onClick={() => navigate('/dashboard')} className="btn btn-secondary" style={{ marginLeft: '10px' }}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        {reviewHeader}
        {pipelineStrip}
        {isProcessing && (
          <div className="processing-banner" role="status">
            <span className="processing-banner-text">Processing in progress.</span>
            <span> Use the refresh button to see the latest status.</span>
          </div>
        )}
        {validation && (
          <div className={`validation-status ${validation.validation_status.toLowerCase()}`}>
            <strong>Validation Status:</strong> {validation.validation_status}
            {validation.validation_errors.length > 0 && (
              <ul>
                {validation.validation_errors.map((error, idx) => (
                  <li key={idx}>
                    <strong>{error.field}:</strong> {error.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className="fields-container">
          {Object.keys(extraction.structured_data || {}).length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              <p><strong>No structured data extracted.</strong></p>
              <p style={{ marginTop: '10px', fontSize: '14px' }}>
                The document was processed but no fields were extracted. This may happen if:
              </p>
              <ul style={{ textAlign: 'left', display: 'inline-block', marginTop: '10px' }}>
                <li>The document format is not recognized</li>
                <li>The OCR text extraction was incomplete</li>
                <li>The LLM extraction failed</li>
              </ul>
              {extraction.extraction_metadata && (
                <div style={{ marginTop: '15px', padding: '10px', background: '#fff3cd', borderRadius: '4px', fontSize: '12px', textAlign: 'left' }}>
                  <strong>Extraction Details:</strong>
                  <ul style={{ marginTop: '5px', paddingLeft: '20px', marginBottom: '0' }}>
                    <li>{`OCR Provider: ${extraction.extraction_metadata.ocr_provider || 'Unknown'}`}</li>
                    <li>{`LLM Provider: ${extraction.extraction_metadata.llm_provider || 'N/A'}`}</li>
                    <li>{`LLM Model: ${extraction.extraction_metadata.llm_model || 'N/A'}`}</li>
                    {extraction.extraction_metadata.error ? (
                      <li style={{ color: '#dc3545', fontWeight: 'bold' }}>{`Error: ${extraction.extraction_metadata.error}`}</li>
                    ) : null}
                    {extraction.extraction_metadata.fallback ? (
                      <li style={{ color: '#856404' }}>{`Fallback: ${extraction.extraction_metadata.fallback}`}</li>
                    ) : null}
                  </ul>
                </div>
              )}
              {extraction.raw_text && (
                <div style={{ marginTop: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '4px', textAlign: 'left' }}>
                  <strong>Extracted Text:</strong>
                  <pre style={{ marginTop: '10px', whiteSpace: 'pre-wrap', fontSize: '12px', maxHeight: '200px', overflow: 'auto' }}>
                    {extraction.raw_text.substring(0, RAW_TEXT_PREVIEW_LENGTH)}{extraction.raw_text.length > RAW_TEXT_PREVIEW_LENGTH ? '...' : ''}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            Object.entries(extraction.structured_data || {}).map(([field, value]) => {
              const confidence = extraction.confidence_scores[field] || 0;
              return (
                <div key={field} className="field-group">
                  <label>
                    {field.replace(/_/g, ' ').toUpperCase()}
                    <span className={`confidence-badge ${getConfidenceClass(confidence)}`}>
                      {Math.round(confidence * 100)}%
                    </span>
                  </label>
                  <input
                    type="text"
                    value={corrections[field] || (value as string) || ''}
                    onChange={(e) => setCorrection(field, e.target.value)}
                  />
                  <div className="confidence-bar">
                    <div
                      className={`confidence-fill ${getConfidenceClass(confidence)}`}
                      style={{ width: `${confidence * 100}%` }}
                    />
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="review-actions">
          <button
            type="button"
            onClick={handleRestartProcessing}
            className="btn btn-restart"
            disabled={restartingProcessing}
            title="Re-run extraction pipeline"
          >
            {restartingProcessing ? 'Processing…' : 'Restart processing'}
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Review'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentReview;


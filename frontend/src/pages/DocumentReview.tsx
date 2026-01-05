import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DocumentReview.css';

interface Extraction {
  id: string;
  document_id: string;
  extraction_method: string;
  raw_text?: string;
  structured_data: { [key: string]: any };
  confidence_scores: { [key: string]: number };
  extracted_at: string;
  extraction_metadata?: { [key: string]: any };
}

interface Validation {
  validation_status: string;
  validation_errors: Array<{ field: string; message: string; severity: string }>;
}

const DocumentReview: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const [extraction, setExtraction] = useState<Extraction | null>(null);
  const [validation, setValidation] = useState<Validation | null>(null);
  const [corrections, setCorrections] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchData();
  }, [documentId]);

  const fetchData = async () => {
    try {
      // Only fetch extraction first - validation requires extraction to exist
      const extractionRes = await axios.get(`/api/v1/documents/${documentId}/extraction`).catch(() => null);

      if (extractionRes) {
        setExtraction(extractionRes.data);
        // Initialize corrections with extracted data
        setCorrections(extractionRes.data.structured_data || {});
        
        // Only fetch validation if structured_data exists (validation requires structured data)
        const hasStructuredData = extractionRes.data.structured_data && 
                                  Object.keys(extractionRes.data.structured_data).length > 0;
        
        if (hasStructuredData) {
          try {
            const validationRes = await axios.get(`/api/v1/documents/${documentId}/validation`);
            if (validationRes) {
              setValidation(validationRes.data);
            }
          } catch (error: any) {
            // Silently ignore validation errors - it's not critical for review
            console.warn('Validation fetch failed:', error.response?.data?.detail);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (field: string, value: string) => {
    setCorrections((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.post(`/api/v1/documents/${documentId}/review`, {
        corrections,
        review_notes: '',
      });
      navigate('/dashboard');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save review');
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceClass = (confidence: number) => {
    if (confidence >= 0.7) return 'high';
    if (confidence >= 0.4) return 'medium';
    return 'low';
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

  const triggerExtraction = async () => {
    setLoading(true);
    try {
      await axios.post(`/api/v1/documents/${documentId}/extraction/retry`);
      // Wait a moment then refresh
      setTimeout(() => {
        fetchData();
      }, 2000);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to trigger extraction');
      setLoading(false);
    }
  };

  if (!extraction) {
    return (
      <div className="container">
        <div className="card">
          <h2>Review Document</h2>
          <p>Extraction not found. The document may still be processing.</p>
          <div style={{ marginTop: '20px' }}>
            <button onClick={triggerExtraction} className="btn btn-primary" disabled={loading}>
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
        <h2>Review Document</h2>
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
                    <li>OCR Provider: {extraction.extraction_metadata.ocr_provider || 'Unknown'}</li>
                    <li>LLM Provider: {extraction.extraction_metadata.llm_provider || 'N/A'}</li>
                    <li>LLM Model: {extraction.extraction_metadata.llm_model || 'N/A'}</li>
                    {extraction.extraction_metadata.error && (
                      <li style={{ color: '#dc3545', fontWeight: 'bold' }}>
                        <strong>Error:</strong> {extraction.extraction_metadata.error}
                      </li>
                    )}
                    {extraction.extraction_metadata.fallback && (
                      <li style={{ color: '#856404' }}>
                        <strong>Fallback:</strong> {extraction.extraction_metadata.fallback}
                      </li>
                    )}
                  </ul>
                </div>
              )}
              {extraction.raw_text && (
                <div style={{ marginTop: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '4px', textAlign: 'left' }}>
                  <strong>Extracted Text:</strong>
                  <pre style={{ marginTop: '10px', whiteSpace: 'pre-wrap', fontSize: '12px', maxHeight: '200px', overflow: 'auto' }}>
                    {extraction.raw_text.substring(0, 500)}{extraction.raw_text.length > 500 ? '...' : ''}
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
                    value={corrections[field] || value || ''}
                    onChange={(e) => handleFieldChange(field, e.target.value)}
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


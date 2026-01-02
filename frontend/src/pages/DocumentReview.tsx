import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DocumentReview.css';

interface Extraction {
  structured_data: { [key: string]: any };
  confidence_scores: { [key: string]: number };
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
        
        // Now fetch validation if extraction exists
        const validationRes = await axios.get(`/api/v1/documents/${documentId}/validation`).catch(() => null);
        if (validationRes) {
          setValidation(validationRes.data);
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
          {Object.entries(extraction.structured_data || {}).map(([field, value]) => {
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
          })}
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


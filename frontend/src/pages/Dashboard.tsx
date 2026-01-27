import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import './Dashboard.css';

interface Document {
  id: string;
  original_filename: string;
  status: string;
  document_type: string | null;
  uploaded_at: string;
  file_size: number;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [restartingDocumentId, setRestartingDocumentId] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const refreshDocuments = async () => {
    if (refreshing) return;
    setRefreshing(true);
    try {
      const response = await axios.get('/api/v1/documents?limit=50');
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('Failed to fetch documents', error);
    } finally {
      setRefreshing(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/v1/documents?limit=50');
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('Failed to fetch documents', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = async (documentId: string) => {
    setRestartingDocumentId(documentId);
    try {
      await axios.post(`/api/v1/documents/${documentId}/reprocess`);
      await refreshDocuments();
    } catch (error: any) {
      alert(error.response?.data?.detail || error.response?.data?.message || 'Failed to restart processing');
    } finally {
      setRestartingDocumentId(null);
    }
  };

  const handleDelete = async (documentId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`/api/v1/documents/${documentId}`);
      refreshDocuments();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete document');
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: { [key: string]: string } = {
      UPLOADED: 'badge-info',
      PROCESSING: 'badge-warning',
      EXTRACTED: 'badge-success',
      VALIDATED: 'badge-success',
      REVIEWED: 'badge-success',
      EXPORTED: 'badge-success',
      FAILED: 'badge-danger',
    };
    return badges[status] || 'badge-secondary';
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <h1>DocFlow AI</h1>
            <div className="header-actions">
              <span className="user-info">{user?.email}</span>
              <button onClick={logout} className="btn btn-secondary">
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container">
        <div className="dashboard-actions">
          <Link to="/upload" className="btn btn-primary">
            Upload Document
          </Link>
        </div>

        <div className="card">
          <div className="card-header-row">
            <h2>Documents</h2>
            <button
              type="button"
              className="btn-refresh"
              onClick={refreshDocuments}
              disabled={refreshing}
              title="Refresh status"
              aria-label="Refresh document list"
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
          {loading ? (
            <p>Loading...</p>
          ) : documents.length === 0 ? (
            <p>No documents found. Upload your first document to get started.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.original_filename}</td>
                    <td>{doc.document_type || 'Unknown'}</td>
                    <td className="status-cell">
                      <span className={`badge ${getStatusBadge(doc.status)} ${doc.status === 'PROCESSING' ? 'badge-processing' : ''}`}>
                        {doc.status}
                      </span>
                      {doc.status === 'PROCESSING' && (
                        <div className="status-progress" role="progressbar" aria-label="Processing" aria-valuetext="Processing">
                          <div className="status-progress-bar" />
                        </div>
                      )}
                    </td>
                    <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                    <td>
                      <div className="row-actions">
                        <Link
                          to={`/review/${doc.id}`}
                          className="btn btn-secondary btn-sm"
                        >
                          Review
                        </Link>
                        <button
                          type="button"
                          onClick={() => handleRestart(doc.id)}
                          className="btn btn-restart btn-sm"
                          disabled={restartingDocumentId === doc.id}
                          title="Restart processing (re-run extraction)"
                          aria-label={`Restart processing for ${doc.original_filename}`}
                        >
                          {restartingDocumentId === doc.id ? 'Processing…' : 'Restart'}
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id, doc.original_filename)}
                          className="btn btn-danger btn-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;


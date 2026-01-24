import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useDocuments } from '../hooks/useDocuments';
import { getStatusBadge } from '../constants';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const { documents, loading, deleteDocument } = useDocuments({ limit: 50 });

  const handleDelete = async (documentId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) return;
    try {
      await deleteDocument(documentId);
    } catch (e) {
      alert((e as Error).message || 'Failed to delete document');
    }
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
          <h2>Documents</h2>
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
                    <td>
                      <span className={`badge ${getStatusBadge(doc.status)}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <Link
                          to={`/review/${doc.id}`}
                          className="btn btn-secondary"
                          style={{ fontSize: '12px', padding: '6px 12px' }}
                        >
                          Review
                        </Link>
                        <button
                          onClick={() => handleDelete(doc.id, doc.original_filename)}
                          className="btn btn-danger"
                          style={{ fontSize: '12px', padding: '6px 12px' }}
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


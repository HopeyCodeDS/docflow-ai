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

  useEffect(() => {
    fetchDocuments();
  }, []);

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
                      <Link
                        to={`/review/${doc.id}`}
                        className="btn btn-secondary"
                        style={{ fontSize: '12px', padding: '6px 12px' }}
                      >
                        Review
                      </Link>
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


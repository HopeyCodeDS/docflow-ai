import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useDocuments, type DocumentFilters } from '../hooks/useDocuments';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { getStatusBadge, DOCUMENT_STATUSES } from '../constants';
import client from '../api/client';
import './Dashboard.css';

const SEARCH_DEBOUNCE_MS = 300;

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchInput, setSearchInput] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const debouncedSearch = useDebouncedValue(searchInput.trim(), SEARCH_DEBOUNCE_MS);

  const filters: DocumentFilters = useMemo(
    () => ({
      ...(statusFilter && { status: statusFilter }),
      ...(debouncedSearch && { filename: debouncedSearch }),
      ...(dateFrom && { date_from: dateFrom }),
      ...(dateTo && { date_to: dateTo }),
    }),
    [statusFilter, debouncedSearch, dateFrom, dateTo]
  );

  const hasActiveFilters = Boolean(statusFilter || searchInput.trim() || dateFrom || dateTo);

  const { documents, total, loading, deleteDocument, refresh } = useDocuments({
    limit: 50,
    filters: hasActiveFilters ? filters : undefined,
  });

  const [refreshing, setRefreshing] = useState(false);
  const [restartingDocumentId, setRestartingDocumentId] = useState<string | null>(null);

  const clearFilters = () => {
    setStatusFilter('');
    setSearchInput('');
    setDateFrom('');
    setDateTo('');
  };

  const refreshDocuments = async () => {
    if (refreshing) return;
    setRefreshing(true);
    try {
      await refresh();
    } catch (error) {
      console.error('Failed to fetch documents', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleRestart = async (documentId: string) => {
    setRestartingDocumentId(documentId);
    try {
      await client.post(`/documents/${documentId}/reprocess`);
      await refreshDocuments();
    } catch (error: unknown) {
      alert(error instanceof Error ? error.message : 'Failed to restart processing');
    } finally {
      setRestartingDocumentId(null);
    }
  };

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
          <Link
            to="/upload"
            className="btn btn-primary"
            style={{ textDecoration: 'none' }}
          >
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

          <div className="dashboard-filters" role="search" aria-label="Filter documents">
            <div className="dashboard-filters-row">
              <label className="filter-label" htmlFor="filter-status">
                Status
              </label>
              <select
                id="filter-status"
                className="filter-select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                aria-label="Filter by status"
              >
                <option value="">All statuses</option>
                {DOCUMENT_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>

              <label className="filter-label" htmlFor="filter-filename">
                Filename
              </label>
              <input
                id="filter-filename"
                type="search"
                className="filter-input"
                placeholder="Search by filename…"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                aria-label="Search by filename"
                autoComplete="off"
              />

              <label className="filter-label" htmlFor="filter-date-from">
                From
              </label>
              <input
                id="filter-date-from"
                type="date"
                className="filter-input filter-date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                aria-label="Uploaded from date"
              />

              <label className="filter-label" htmlFor="filter-date-to">
                To
              </label>
              <input
                id="filter-date-to"
                type="date"
                className="filter-input filter-date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                aria-label="Uploaded to date"
              />

              {hasActiveFilters && (
                <button
                  type="button"
                  className="btn btn-secondary btn-clear-filters"
                  onClick={clearFilters}
                  aria-label="Clear all filters"
                >
                  Clear filters
                </button>
              )}
            </div>
          </div>

          {loading ? (
            <p>Loading...</p>
          ) : documents.length === 0 ? (
            <p>
              {hasActiveFilters
                ? 'No documents match the current filters. Try adjusting or clear filters.'
                : 'No documents found. Upload your first document to get started.'}
            </p>
          ) : (
            <>
              {hasActiveFilters && (
                <p className="dashboard-results-summary" aria-live="polite">
                  Showing {documents.length} of {total} document{total !== 1 ? 's' : ''}
                </p>
              )}
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
                          style={{ textDecoration: 'none' }}
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
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;


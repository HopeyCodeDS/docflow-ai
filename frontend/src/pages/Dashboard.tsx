import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  FileText,
  Loader2,
  CheckCircle,
  AlertCircle,
  Clock,
  Search,
  RefreshCw,
  Eye,
  RotateCw,
  Trash2,
  Upload,
  FileStack,
} from 'lucide-react';
import { useDocuments, type DocumentFilters } from '../hooks/useDocuments';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { getDocumentTypeLabel, DOCUMENT_STATUSES } from '../constants';
import client from '../api/client';
import type { Document } from '../services/documents';
import TopBar from '../components/layout/TopBar';
import StatsCard from '../components/ui/StatsCard';
import { Card } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import DataTable from '../components/ui/DataTable';
import type { Column } from '../components/ui/DataTable';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import { SkeletonTableRow } from '../components/ui/Skeleton';

const SEARCH_DEBOUNCE_MS = 300;

const STATUS_BADGE_MAP: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'secondary'> = {
  UPLOADED: 'info',
  PROCESSING: 'warning',
  EXTRACTED: 'success',
  VALIDATED: 'success',
  REVIEWED: 'success',
  EXPORTED: 'success',
  FAILED: 'danger',
};

const Dashboard: React.FC = () => {
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
  const [deleteModal, setDeleteModal] = useState<{ id: string; name: string } | null>(null);

  // KPI stats
  const stats = useMemo(() => {
    const all = documents;
    return {
      total: total,
      processing: all.filter((d) => d.status === 'PROCESSING').length,
      completed: all.filter((d) =>
        ['EXTRACTED', 'VALIDATED', 'REVIEWED', 'EXPORTED'].includes(d.status)
      ).length,
      failed: all.filter((d) => d.status === 'FAILED').length,
    };
  }, [documents, total]);

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
      toast.success('Reprocessing started');
      await refreshDocuments();
    } catch (error: unknown) {
      toast.error(error instanceof Error ? error.message : 'Failed to restart processing');
    } finally {
      setRestartingDocumentId(null);
    }
  };

  const handleDelete = async () => {
    if (!deleteModal) return;
    try {
      await deleteDocument(deleteModal.id);
      toast.success('Document deleted');
      setDeleteModal(null);
    } catch (e) {
      toast.error((e as Error).message || 'Failed to delete document');
    }
  };

  const columns: Column<Document>[] = [
    {
      key: 'filename',
      header: 'Filename',
      render: (doc) => (
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-slate-400 flex-shrink-0" />
          <span className="font-medium text-slate-900 truncate max-w-[200px]">
            {doc.original_filename}
          </span>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Type',
      render: (doc) => (
        <Badge variant="secondary">{getDocumentTypeLabel(doc.document_type)}</Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (doc) => (
        <div className="flex items-center gap-2">
          <Badge variant={STATUS_BADGE_MAP[doc.status] ?? 'secondary'} dot>
            {doc.status}
          </Badge>
          {doc.status === 'PROCESSING' && (
            <Loader2 className="h-3.5 w-3.5 text-amber-500 animate-spin" />
          )}
        </div>
      ),
    },
    {
      key: 'uploaded',
      header: 'Uploaded',
      render: (doc) => (
        <span className="text-slate-500">
          {new Date(doc.uploaded_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      className: 'text-right',
      render: (doc) => (
        <div className="flex items-center justify-end gap-1">
          <Link
            to={`/review/${doc.id}`}
            className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-slate-500 hover:text-brand-600 hover:bg-brand-50 transition-colors"
            title="Review"
          >
            <Eye className="h-4 w-4" />
          </Link>
          <button
            type="button"
            onClick={() => handleRestart(doc.id)}
            disabled={restartingDocumentId === doc.id}
            className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-slate-500 hover:text-amber-600 hover:bg-amber-50 transition-colors disabled:opacity-50"
            title="Restart processing"
          >
            <RotateCw
              className={`h-4 w-4 ${restartingDocumentId === doc.id ? 'animate-spin' : ''}`}
            />
          </button>
          <button
            type="button"
            onClick={() => setDeleteModal({ id: doc.id, name: doc.original_filename })}
            className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 transition-colors"
            title="Delete"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ];

  const statusOptions = DOCUMENT_STATUSES.map((s) => ({ value: s, label: s }));

  return (
    <>
      <TopBar
        title="Dashboard"
        subtitle="Manage and monitor your documents"
        actions={
          <div className="flex items-center gap-3">
            <Button variant="ghost" icon={<RefreshCw className="h-4 w-4" />} onClick={refreshDocuments} loading={refreshing} size="sm">
              Refresh
            </Button>
            <Link to="/upload">
              <Button icon={<Upload className="h-4 w-4" />} size="sm">
                Upload Document
              </Button>
            </Link>
          </div>
        }
      />

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatsCard
          label="Total Documents"
          value={stats.total}
          icon={<FileText className="h-6 w-6" />}
          iconBg="bg-brand-50"
          iconColor="text-brand-600"
        />
        <StatsCard
          label="Processing"
          value={stats.processing}
          icon={stats.processing > 0
            ? <Loader2 className="h-6 w-6 animate-spin" />
            : <Clock className="h-6 w-6" />
          }
          iconBg="bg-amber-50"
          iconColor="text-amber-600"
        />
        <StatsCard
          label="Completed"
          value={stats.completed}
          icon={<CheckCircle className="h-6 w-6" />}
          iconBg="bg-emerald-50"
          iconColor="text-emerald-600"
        />
        <StatsCard
          label="Failed"
          value={stats.failed}
          icon={<AlertCircle className="h-6 w-6" />}
          iconBg="bg-red-50"
          iconColor="text-red-600"
        />
      </div>

      {/* Filters + Table */}
      <Card padding={false}>
        <div className="p-4 border-b border-slate-200">
          <div className="flex flex-wrap items-end gap-3">
            <div className="w-48">
              <Select
                label="Status"
                options={statusOptions}
                placeholder="All statuses"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              />
            </div>
            <div className="w-56">
              <Input
                label="Search"
                type="search"
                placeholder="Search by filename..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                icon={<Search className="h-4 w-4" />}
              />
            </div>
            <div className="w-40">
              <Input
                label="From"
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>
            <div className="w-40">
              <Input
                label="To"
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear filters
              </Button>
            )}
          </div>
          {hasActiveFilters && !loading && (
            <p className="mt-2 text-xs text-slate-500">
              Showing {documents.length} of {total} document{total !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        <DataTable
          columns={columns}
          data={documents}
          keyExtractor={(doc) => doc.id}
          loading={loading}
          loadingRows={
            <>
              {Array.from({ length: 5 }).map((_, i) => (
                <SkeletonTableRow key={i} columns={5} />
              ))}
            </>
          }
          emptyState={
            <EmptyState
              icon={<FileStack className="h-8 w-8" />}
              title={hasActiveFilters ? 'No matches' : 'No documents yet'}
              description={
                hasActiveFilters
                  ? 'Try adjusting your filters or clear them to see all documents.'
                  : 'Upload your first document to get started with intelligent extraction.'
              }
              action={
                hasActiveFilters ? (
                  <Button variant="secondary" size="sm" onClick={clearFilters}>
                    Clear filters
                  </Button>
                ) : (
                  <Link to="/upload">
                    <Button size="sm" icon={<Upload className="h-4 w-4" />}>
                      Upload Document
                    </Button>
                  </Link>
                )
              }
            />
          }
        />
      </Card>

      {/* Delete confirmation modal */}
      <Modal
        open={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Delete document"
        description={`Are you sure you want to delete "${deleteModal?.name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        confirmVariant="danger"
        onConfirm={handleDelete}
      />
    </>
  );
};

export default Dashboard;

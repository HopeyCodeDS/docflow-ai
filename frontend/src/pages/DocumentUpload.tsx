import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { ArrowLeft } from 'lucide-react';
import * as documentsService from '../services/documents';
import TopBar from '../components/layout/TopBar';
import { Card } from '../components/ui/Card';
import Button from '../components/ui/Button';
import DropZone from '../components/ui/DropZone';

const DocumentUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error('Please select a file');
      return;
    }
    setUploading(true);
    try {
      await documentsService.uploadDocument(file);
      toast.success('Document uploaded successfully');
      navigate('/dashboard');
    } catch (err) {
      toast.error((err as Error).message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <TopBar
        title="Upload Document"
        subtitle="Upload a document for intelligent extraction and classification"
        actions={
          <Link to="/dashboard">
            <Button variant="ghost" size="sm" icon={<ArrowLeft className="h-4 w-4" />}>
              Back to Dashboard
            </Button>
          </Link>
        }
      />

      <div className="max-w-xl">
        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            <DropZone
              accept=".pdf,.png,.jpg,.jpeg"
              file={file}
              onFileSelect={setFile}
              onFileClear={() => setFile(null)}
            />

            <Button
              type="submit"
              loading={uploading}
              disabled={!file}
              className="w-full"
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </Button>
          </form>
        </Card>
      </div>
    </>
  );
};

export default DocumentUpload;

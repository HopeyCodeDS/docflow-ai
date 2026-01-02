import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DocumentUpload.css';

const DocumentUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/api/v1/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Extraction is now automatically triggered on the backend
      // Navigate to dashboard - extraction will complete in background
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Upload error:', err);
      let errorMessage = 'Upload failed';
      
      if (err.response?.data) {
        // Try different error formats
        errorMessage = err.response.data.detail || 
                      err.response.data.message || 
                      err.response.data.error?.message ||
                      JSON.stringify(err.response.data);
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Upload Document</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Select Document (PDF, PNG, JPG)</label>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              required
            />
          </div>
          {file && (
            <div className="file-info">
              <p>Selected: {file.name}</p>
              <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
          <button
            type="submit"
            className="btn btn-primary"
            disabled={uploading || !file}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default DocumentUpload;


import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import clsx from 'clsx';
import Badge from './Badge';

interface DropZoneProps {
  accept: string;
  file: File | null;
  onFileSelect: (file: File) => void;
  onFileClear: () => void;
}

const DropZone: React.FC<DropZoneProps> = ({ accept, file, onFileSelect, onFileClear }) => {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) onFileSelect(dropped);
    },
    [onFileSelect]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) onFileSelect(selected);
  };

  if (file) {
    return (
      <div className="border border-slate-200 rounded-xl p-4 flex items-center gap-4">
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-brand-50 flex items-center justify-center text-brand-600">
          <FileText className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-900 truncate">{file.name}</p>
          <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
        <button
          type="button"
          onClick={onFileClear}
          className="flex-shrink-0 text-slate-400 hover:text-slate-600 transition-colors p-1"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      className={clsx(
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
        dragOver
          ? 'border-brand-400 bg-brand-50'
          : 'border-slate-300 hover:border-brand-400 hover:bg-slate-50'
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
      <div className="flex flex-col items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-brand-50 flex items-center justify-center text-brand-600">
          <Upload className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm font-medium text-slate-900">
            Drop your file here, or <span className="text-brand-600">browse</span>
          </p>
          <p className="text-xs text-slate-500 mt-1">Supports PDF, PNG, JPG</p>
        </div>
        <div className="flex gap-2 mt-1">
          <Badge variant="secondary">PDF</Badge>
          <Badge variant="secondary">PNG</Badge>
          <Badge variant="secondary">JPG</Badge>
        </div>
      </div>
    </div>
  );
};

export default DropZone;

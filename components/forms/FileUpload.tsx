"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Loader2 } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (files: File | File[]) => Promise<void>;
  multiple?: boolean;
  acceptedFileTypes?: string[];
  maxFileSize?: number;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  multiple = false,
  acceptedFileTypes = ['.sav'],
  maxFileSize = 10 * 1024 * 1024, // 10MB default
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      try {
        setError(null);
        setIsLoading(true);

        if (acceptedFiles.length === 0) {
          setError('No files selected');
          return;
        }

        if (!multiple && acceptedFiles.length > 1) {
          setError('Multiple files not allowed');
          return;
        }

        // Validate file types
        const invalidFiles = acceptedFiles.filter(
          (file) => !acceptedFileTypes.some((type) => 
            file.name.toLowerCase().endsWith(type.toLowerCase())
          )
        );

        if (invalidFiles.length > 0) {
          setError(`Invalid file type. Accepted types: ${acceptedFileTypes.join(', ')}`);
          return;
        }

        // Validate file sizes
        const oversizedFiles = acceptedFiles.filter((file) => file.size > maxFileSize);
        if (oversizedFiles.length > 0) {
          setError(`File size exceeds ${maxFileSize / (1024 * 1024)}MB limit`);
          return;
        }

        await onFileSelect(multiple ? acceptedFiles : acceptedFiles[0]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred during file upload');
      } finally {
        setIsLoading(false);
      }
    },
    [onFileSelect, multiple, acceptedFileTypes, maxFileSize]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple,
    accept: acceptedFileTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize: maxFileSize,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6
          flex flex-col items-center justify-center
          transition-all duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          cursor-pointer hover:bg-gray-100
        `}
        data-testid="drop-zone"
      >
        <input {...getInputProps()} data-testid="file-input" />
        {isLoading ? (
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" data-testid="loading-indicator" />
        ) : (
          <Upload className="h-8 w-8 text-gray-500" />
        )}
        <p className="text-gray-600 mt-2 text-center">
          {isDragActive ? (
            'Drop the files here...'
          ) : (
            <>
              Drag and drop your {multiple ? 'files' : 'file'} here
              <br />
              or click to browse
            </>
          )}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Accepted files: {acceptedFileTypes.join(', ')}
        </p>
      </div>
      {error && (
        <p className="text-red-500 mt-2 text-sm" data-testid="error-message">
          {error}
        </p>
      )}
    </div>
  );
}; 
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { FileUpload } from '../../../components/forms/FileUpload';
import * as ReactDropzone from 'react-dropzone';
import '@testing-library/jest-dom';

// Mock react-dropzone
jest.mock('react-dropzone', () => ({
  useDropzone: jest.fn(),
}));

// Constants
const SPSS_FILE_TYPE = 'application/x-spss-sav';
const DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Type for file selection callback
type FileSelectCallback = (files: File | File[]) => Promise<void>;

describe('FileUpload Component', () => {
  const mockOnFileSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with initial state', () => {
    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(() => ({
      getRootProps: () => ({ 'data-testid': 'drop-zone' }),
      getInputProps: () => ({ 'data-testid': 'file-input' }),
      isDragActive: false,
    }));

    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    expect(screen.getByText(/drag and drop your file here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
  });

  it('handles single file selection', async () => {
    const file = new File(['test'], 'test.sav', { type: 'application/x-spss-sav' });
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    await act(async () => {
      dropHandler([file]);
    });

    expect(mockOnFileSelect).toHaveBeenCalledWith(file);
  });

  it('handles multiple file selection', async () => {
    const files = [
      new File(['test1'], 'test1.sav', { type: 'application/x-spss-sav' }),
      new File(['test2'], 'test2.sav', { type: 'application/x-spss-sav' }),
    ];
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} multiple />);
    
    await act(async () => {
      dropHandler(files);
    });

    expect(mockOnFileSelect).toHaveBeenCalledWith(files);
  });

  it('shows error for invalid file type', async () => {
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    await act(async () => {
      dropHandler([file]);
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent(/invalid file type/i);
  });

  it('shows loading state during file processing', async () => {
    const file = new File(['test'], 'test.sav', { type: 'application/x-spss-sav' });
    const mockOnFileSelectWithDelay = jest.fn().mockImplementation(() => new Promise(() => {}));
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelectWithDelay} />);
    
    await act(async () => {
      dropHandler([file]);
    });

    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });

  it('handles empty file selection', async () => {
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    await act(async () => {
      dropHandler([]);
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent(/no files selected/i);
  });

  it('validates file type in multiple file upload', async () => {
    const files = [
      new File(['test1'], 'test1.sav', { type: 'application/x-spss-sav' }),
      new File(['test2'], 'test2.txt', { type: 'text/plain' }),
    ];
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} multiple />);
    
    await act(async () => {
      dropHandler(files);
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent(/invalid file type/i);
  });

  it('handles file size validation', async () => {
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.sav', { type: 'application/x-spss-sav' });
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} maxFileSize={10 * 1024 * 1024} />);
    
    await act(async () => {
      dropHandler([largeFile]);
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent(/file size exceeds/i);
  });

  it('shows drag active state', () => {
    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(() => ({
      getRootProps: () => ({ 'data-testid': 'drop-zone' }),
      getInputProps: () => ({ 'data-testid': 'file-input' }),
      isDragActive: true,
    }));

    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    expect(screen.getByText(/drop the files here/i)).toBeInTheDocument();
  });

  it('handles successful file upload', async () => {
    const file = new File(['test'], 'test.sav', { type: 'application/x-spss-sav' });
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    await act(async () => {
      dropHandler([file]);
    });

    expect(mockOnFileSelect).toHaveBeenCalledWith(file);
  });

  it('handles Promise rejection with custom error message', async () => {
    const file = new File(['test'], 'test.sav', { type: 'application/x-spss-sav' });
    const errorMessage = 'Custom error message';
    const mockOnFileSelectWithError = jest.fn().mockRejectedValue(new Error(errorMessage));
    let dropHandler: (files: File[]) => void;

    (ReactDropzone.useDropzone as jest.Mock).mockImplementation(({ onDrop }) => {
      dropHandler = onDrop;
      return {
        getRootProps: () => ({ 'data-testid': 'drop-zone' }),
        getInputProps: () => ({ 'data-testid': 'file-input' }),
        isDragActive: false,
      };
    });

    render(<FileUpload onFileSelect={mockOnFileSelectWithError} />);
    
    await act(async () => {
      dropHandler([file]);
    });

    expect(screen.getByTestId('error-message')).toHaveTextContent(errorMessage);
  });
}); 
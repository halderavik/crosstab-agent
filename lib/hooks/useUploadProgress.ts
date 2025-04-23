import { useState, useCallback } from "react";

interface UploadProgress {
  progress: number;
  isUploading: boolean;
  error: string | null;
}

export function useUploadProgress() {
  const [state, setState] = useState<UploadProgress>({
    progress: 0,
    isUploading: false,
    error: null,
  });

  const startUpload = useCallback(() => {
    setState({ progress: 0, isUploading: true, error: null });
  }, []);

  const updateProgress = useCallback((progress: number) => {
    setState((prev) => ({ ...prev, progress }));
  }, []);

  const setError = useCallback((error: string) => {
    setState((prev) => ({ ...prev, error, isUploading: false }));
  }, []);

  const completeUpload = useCallback(() => {
    setState((prev) => ({ ...prev, progress: 100, isUploading: false }));
  }, []);

  const reset = useCallback(() => {
    setState({ progress: 0, isUploading: false, error: null });
  }, []);

  return {
    ...state,
    startUpload,
    updateProgress,
    setError,
    completeUpload,
    reset,
  };
} 
"use client";

import { useState } from "react";
import { FileUpload } from "@/components/forms/FileUpload";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function UploadPage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);

  const handleFileAccepted = async (file: File) => {
    try {
      setIsUploading(true);
      
      // Create form data
      const formData = new FormData();
      formData.append("file", file);

      // Upload file
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload file");
      }

      const data = await response.json();
      
      // Show success message
      toast.success("File uploaded successfully");
      
      // Redirect to analyze page with file ID
      router.push(`/analyze?fileId=${data.fileId}`);
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload file. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleError = (error: string) => {
    toast.error(error);
  };

  return (
    <div className="container max-w-2xl py-8">
      <div className="space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Upload SPSS File</h1>
          <p className="text-muted-foreground">
            Upload your SPSS (.sav) file to begin analysis
          </p>
        </div>

        <FileUpload
          onFileAccepted={handleFileAccepted}
          onError={handleError}
          className="w-full"
        />

        <div className="rounded-lg border p-4">
          <h2 className="mb-2 font-semibold">File Requirements</h2>
          <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
            <li>Only .sav files are supported</li>
            <li>Maximum file size: 10MB</li>
            <li>File should contain valid SPSS data</li>
            <li>Variable names should be unique and valid</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 
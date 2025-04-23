import { MainLayout } from "@/components/layout/MainLayout";
import { FileUpload } from "@/components/forms/FileUpload";

export default function Home() {
  const handleFileSelect = (file: File) => {
    console.log('Selected file:', file);
    // TODO: Implement file upload logic
  };

  return (
    <MainLayout>
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)]">
        <h1 className="text-4xl font-bold mb-6">SPSS Analyzer</h1>
        <p className="text-xl text-muted-foreground mb-8">
          Upload your SPSS data and analyze it with AI assistance
        </p>
        <div className="w-full max-w-md">
          <FileUpload onFileSelect={handleFileSelect} />
        </div>
      </div>
    </MainLayout>
  );
} 
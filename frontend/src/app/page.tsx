"use client";

import { useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import DropZone from "@/components/upload/DropZone";
import FilePreview from "@/components/upload/FilePreview";
import EmptyState from "@/components/states/EmptyState";
import AnalyzingState from "@/components/states/AnalyzingState";
import ErrorState from "@/components/states/ErrorState";
import AnalysisView from "@/components/analysis/AnalysisView";
import { useLibrary } from "@/hooks/useLibrary";
import { useAnalysis } from "@/hooks/useAnalysis";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const library = useLibrary();
  const analysis = useAnalysis();

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
  }, []);

  const handleAnalyze = useCallback(() => {
    if (!selectedFile) return;
    analysis.analyze(selectedFile);
    setSelectedFile(null);
  }, [selectedFile, analysis]);

  const handleLibrarySelect = useCallback(
    (id: string) => {
      analysis.loadAnalysis(id);
      setSelectedFile(null);
    },
    [analysis]
  );

  const handleSave = useCallback(async () => {
    if (!analysis.data) return;
    await library.save(analysis.data.analysis_id);
  }, [analysis.data, library]);

  const handleRetry = useCallback(() => {
    analysis.reset();
  }, [analysis]);

  return (
    <div className="h-screen flex flex-col">
      <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          library={library.items}
          activeId={analysis.data?.analysis_id ?? null}
          onSelect={handleLibrarySelect}
          loading={library.loading}
        />

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
            {/* Upload area — always visible when idle or has results */}
            {(analysis.status === "idle" || analysis.status === "results") && (
              <div className="space-y-3">
                <DropZone onFileSelect={handleFileSelect} />
                {selectedFile && (
                  <FilePreview
                    file={selectedFile}
                    onAnalyze={handleAnalyze}
                    onClear={() => setSelectedFile(null)}
                  />
                )}
              </div>
            )}

            {/* State views */}
            {analysis.status === "idle" && !selectedFile && <EmptyState />}

            {analysis.status === "analyzing" && (
              <AnalyzingState filename={analysis.filename} />
            )}

            {analysis.status === "error" && (
              <ErrorState message={analysis.error} onRetry={handleRetry} />
            )}

            {analysis.status === "results" && analysis.data && (
              <AnalysisView data={analysis.data} onSave={handleSave} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

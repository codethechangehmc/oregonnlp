"use client";

import { useCallback, useState } from "react";
import { AnalysisResponse } from "@/lib/types";
import * as api from "@/lib/api";

type Status = "idle" | "analyzing" | "results" | "error";

export function useAnalysis() {
  const [status, setStatus] = useState<Status>("idle");
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [filename, setFilename] = useState("");

  const analyze = useCallback(async (file: File) => {
    setStatus("analyzing");
    setFilename(file.name);
    setError("");
    try {
      const result = await api.analyzeFile(file);
      setData(result);
      setStatus("results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "An unknown error occurred");
      setStatus("error");
    }
  }, []);

  const loadAnalysis = useCallback(async (id: string) => {
    setStatus("analyzing");
    setFilename("");
    setError("");
    try {
      const result = await api.getAnalysis(id);
      setData(result);
      setStatus("results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "An unknown error occurred");
      setStatus("error");
    }
  }, []);

  const reset = useCallback(() => {
    setStatus("idle");
    setData(null);
    setError("");
    setFilename("");
  }, []);

  return { status, data, error, filename, analyze, loadAnalysis, reset };
}

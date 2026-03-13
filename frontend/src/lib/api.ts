import { AnalysisResponse, LibraryItem } from "./types";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  return res.json();
}

export async function analyzeFile(file: File): Promise<AnalysisResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/analyze", { method: "POST", body: form });
  return handleResponse<AnalysisResponse>(res);
}

export async function getAnalysis(id: string): Promise<AnalysisResponse> {
  const res = await fetch(`/api/analyses/${id}`);
  return handleResponse<AnalysisResponse>(res);
}

export async function getLibrary(): Promise<LibraryItem[]> {
  const res = await fetch("/api/library");
  return handleResponse<LibraryItem[]>(res);
}

export async function saveToLibrary(
  id: string,
  title?: string
): Promise<LibraryItem> {
  const res = await fetch(`/api/library/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(title ? { title } : {}),
  });
  return handleResponse<LibraryItem>(res);
}

export async function removeFromLibrary(id: string): Promise<void> {
  const res = await fetch(`/api/library/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
}

export function getPdfUrl(id: string): string {
  return `/api/analyses/${id}/pdf`;
}

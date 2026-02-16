"use client";

import { useCallback, useEffect, useState } from "react";
import { LibraryItem } from "@/lib/types";
import * as api from "@/lib/api";

export function useLibrary() {
  const [items, setItems] = useState<LibraryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await api.getLibrary();
      setItems(data);
    } catch {
      // silently fail — sidebar just shows empty
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const save = useCallback(
    async (id: string, title?: string) => {
      const item = await api.saveToLibrary(id, title);
      setItems((prev) => [item, ...prev.filter((i) => i.id !== id)]);
      return item;
    },
    []
  );

  const remove = useCallback(
    async (id: string) => {
      await api.removeFromLibrary(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
    },
    []
  );

  return { items, loading, refresh, save, remove };
}

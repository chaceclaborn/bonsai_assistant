"use client";

import { useEffect } from "react";
import { useSettings } from "@/lib/useSettings";

/**
 * Reads browser settings and pushes them onto <html> as a CSS variable
 * (--green, the app's accent) and a data-theme attribute. Mounted once in the
 * root layout so the whole app re-skins live when settings change.
 */
export default function ThemeApplier() {
  const { settings } = useSettings();

  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty("--green", settings.accent);
    root.dataset.theme = settings.theme;
  }, [settings.accent, settings.theme]);

  return null;
}

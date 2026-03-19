"use client";

import { createContext, useContext, useCallback } from "react";
import { useLocaleStore } from "./locale-store";
import es from "./es.json";
import en from "./en.json";

export type Locale = "es" | "en";

const translations: Record<Locale, Record<string, unknown>> = { es, en };

function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  return path.split(".").reduce<unknown>((acc, key) => {
    if (acc && typeof acc === "object" && key in (acc as Record<string, unknown>)) {
      return (acc as Record<string, unknown>)[key];
    }
    return undefined;
  }, obj);
}

function interpolate(template: string, params?: Record<string, string | number>): string {
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (_, key) =>
    params[key] !== undefined ? String(params[key]) : `{${key}}`
  );
}

export type TFunction = (key: string, params?: Record<string, string | number>) => string;

const I18nContext = createContext<TFunction>((key) => key);

export function useT(): TFunction {
  return useContext(I18nContext);
}

export function useI18n() {
  const locale = useLocaleStore((s) => s.locale);
  const setLocale = useLocaleStore((s) => s.setLocale);

  const t: TFunction = useCallback(
    (key: string, params?: Record<string, string | number>) => {
      const value = getNestedValue(translations[locale], key);
      if (typeof value === "string") {
        return interpolate(value, params);
      }
      // Return key as fallback
      return key;
    },
    [locale]
  );

  return { t, locale, setLocale };
}

export { I18nContext };

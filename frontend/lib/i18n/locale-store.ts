import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Locale } from "./index";

interface LocaleState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      locale: "es",
      setLocale: (locale) => set({ locale }),
    }),
    {
      name: "extracto-locale",
      storage: createJSONStorage(() => localStorage),
    }
  )
);

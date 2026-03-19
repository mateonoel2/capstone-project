"use client";

import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/sidebar";
import { QuotaBanner } from "@/components/quota-banner";
import { useI18n, I18nContext } from "@/lib/i18n";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";
  const { t } = useI18n();

  if (isLoginPage) {
    return <I18nContext.Provider value={t}>{children}</I18nContext.Provider>;
  }

  return (
    <I18nContext.Provider value={t}>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <QuotaBanner />
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </div>
    </I18nContext.Provider>
  );
}

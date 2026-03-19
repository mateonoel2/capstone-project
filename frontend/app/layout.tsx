import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { QueryProvider } from "@/lib/query-provider";
import { AuthProvider } from "@/components/auth-provider";
import { AppShell } from "@/components/app-shell";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Bank Statement Extraction",
  description: "Extract and verify bank account information from PDF statements",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <QueryProvider>
            <AppShell>{children}</AppShell>
          </QueryProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

"use client";

import { SessionProvider, useSession } from "next-auth/react";
import { useEffect, useRef } from "react";
import { loginToBackend } from "@/lib/api";
import { useExtractionStore } from "@/lib/store";

function BackendAuthSync({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const { backendToken, setBackendAuth, clearBackendAuth } = useExtractionStore();
  const loginAttempted = useRef(false);

  useEffect(() => {
    if (status !== "authenticated" || !session?.githubAccessToken) return;
    if (backendToken || loginAttempted.current) return;

    loginAttempted.current = true;

    loginToBackend(session.githubAccessToken)
      .then((res) => {
        setBackendAuth(res.access_token, res.user);
      })
      .catch((err) => {
        console.error("Backend login failed:", err);
        clearBackendAuth();
      });
  }, [status, session, backendToken, setBackendAuth, clearBackendAuth]);

  // Reset loginAttempted when session changes (e.g., re-login)
  useEffect(() => {
    if (status === "unauthenticated") {
      loginAttempted.current = false;
      clearBackendAuth();
    }
  }, [status, clearBackendAuth]);

  return <>{children}</>;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <BackendAuthSync>{children}</BackendAuthSync>
    </SessionProvider>
  );
}

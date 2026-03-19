"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "next-auth/react";
import { FileUp, BarChart3, Settings, Users, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useExtractionStore } from "@/lib/store";

const navigation = [
  { name: "Extraer PDF", href: "/", icon: FileUp },
  { name: "Extractores", href: "/extractors", icon: Settings },
  { name: "Dashboard", href: "/dashboard", icon: BarChart3 },
];

const adminNavigation = [
  { name: "Usuarios", href: "/admin/users", icon: Users },
];

export function Sidebar() {
  const pathname = usePathname();
  const backendUser = useExtractionStore((s) => s.backendUser);
  const clearBackendAuth = useExtractionStore((s) => s.clearBackendAuth);
  const isAdmin = backendUser?.role === "admin";

  const handleSignOut = () => {
    clearBackendAuth();
    signOut({ callbackUrl: "/login" });
  };

  const allNavigation = isAdmin
    ? [...navigation, ...adminNavigation]
    : navigation;

  return (
    <div className="flex h-screen w-64 flex-col bg-gray-900 text-white">
      <div className="flex h-16 items-center justify-center border-b border-gray-800">
        <h1 className="text-xl font-bold">Bank Extraction</h1>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {allNavigation.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-gray-800 p-4">
        {backendUser ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              {backendUser.avatar_url && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={backendUser.avatar_url}
                  alt={backendUser.github_username}
                  className="h-8 w-8 rounded-full"
                />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-white">
                  {backendUser.github_username}
                </p>
                {isAdmin && (
                  <span className="inline-flex rounded bg-yellow-500/20 px-1.5 py-0.5 text-xs font-medium text-yellow-300">
                    Admin
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={handleSignOut}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-800 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
              Cerrar sesión
            </button>
          </div>
        ) : (
          <p className="text-xs text-gray-400">Capstone Project v1.0</p>
        )}
      </div>
    </div>
  );
}

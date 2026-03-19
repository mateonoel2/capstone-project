"use client";

import { useState } from "react";
import { useApiTokens, useCreateApiToken, useRevokeApiToken } from "@/lib/hooks";
import { useT } from "@/lib/i18n";
import type { CreateTokenResponse } from "@/lib/api";
import { Key } from "lucide-react";

function TokenStatus({ token }: { token: { is_revoked: boolean; expires_at: string | null } }) {
  const t = useT();
  if (token.is_revoked) {
    return (
      <span className="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800">
        {t("tokens.revoked")}
      </span>
    );
  }
  if (token.expires_at && new Date(token.expires_at) < new Date()) {
    return (
      <span className="inline-flex rounded-full bg-yellow-100 px-2 text-xs font-semibold leading-5 text-yellow-800">
        {t("tokens.expired")}
      </span>
    );
  }
  return (
    <span className="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800">
      {t("tokens.active")}
    </span>
  );
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function TokensPage() {
  const t = useT();
  const { data: tokens, isLoading, error } = useApiTokens();
  const createMutation = useCreateApiToken();
  const revokeMutation = useRevokeApiToken();

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [tokenName, setTokenName] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [createdToken, setCreatedToken] = useState<CreateTokenResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokenName.trim()) return;
    try {
      const result = await createMutation.mutateAsync({
        name: tokenName.trim(),
        expires_at: expiresAt || null,
      });
      setCreatedToken(result);
      setTokenName("");
      setExpiresAt("");
      setShowCreateForm(false);
    } catch {
      // error shown via mutation state
    }
  };

  const handleCopy = async () => {
    if (!createdToken) return;
    await navigator.clipboard.writeText(createdToken.token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRevoke = async (tokenId: number, name: string) => {
    if (!confirm(t("tokens.confirmRevoke", { name }))) return;
    await revokeMutation.mutateAsync(tokenId);
  };

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t("tokens.title")}</h1>
          <p className="mt-1 text-sm text-gray-500">{t("tokens.subtitle")}</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          {t("tokens.createToken")}
        </button>
      </div>

      {createMutation.error && (
        <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
          {createMutation.error.message}
        </div>
      )}

      {/* Token reveal modal */}
      {createdToken && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="mx-4 w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900">{t("tokens.tokenCreated")}</h3>
            <p className="mt-2 text-sm font-medium text-amber-700">{t("tokens.copyWarning")}</p>
            <div className="mt-4 flex items-center gap-2">
              <input
                type="text"
                readOnly
                value={createdToken.token}
                className="block w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 font-mono text-sm shadow-sm"
              />
              <button
                onClick={handleCopy}
                className="shrink-0 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
              >
                {copied ? t("tokens.copied") : t("tokens.copy")}
              </button>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setCreatedToken(null);
                  setCopied(false);
                }}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                {t("tokens.close")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create form */}
      {showCreateForm && (
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="mb-3 text-sm font-medium text-gray-900">{t("tokens.newToken")}</h3>
          <form onSubmit={handleCreate} className="flex items-end gap-3">
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700">{t("tokens.name")}</label>
              <input
                type="text"
                value={tokenName}
                onChange={(e) => setTokenName(e.target.value)}
                placeholder={t("tokens.namePlaceholder")}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700">
                {t("tokens.expiry")}
              </label>
              <input
                type="datetime-local"
                value={expiresAt}
                onChange={(e) => setExpiresAt(e.target.value)}
                className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
            >
              {createMutation.isPending ? t("tokens.creating") : t("tokens.create")}
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              {t("tokens.cancel")}
            </button>
          </form>
        </div>
      )}

      {isLoading && <p className="text-sm text-gray-500">{t("tokens.loading")}</p>}
      {error && <p className="text-sm text-red-600">{t("tokens.loadError")}</p>}

      {tokens && tokens.length === 0 && !showCreateForm && (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <Key className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">{t("tokens.emptyTitle")}</h3>
          <p className="mt-2 max-w-md mx-auto text-sm text-gray-500">
            {t("tokens.emptyDescription")}
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="mt-6 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
          >
            {t("tokens.createToken")}
          </button>
        </div>
      )}

      {tokens && tokens.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("tokens.nameColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("tokens.createdColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("tokens.expiresColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("tokens.lastUsedColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("tokens.statusColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("tokens.actionsColumn")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tokens.map((token) => (
                <tr key={token.id}>
                  <td className="whitespace-nowrap px-6 py-4">
                    <span className="text-sm font-medium text-gray-900">{token.name}</span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {formatDate(token.created_at)}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {token.expires_at ? formatDate(token.expires_at) : t("tokens.noExpiry")}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {token.last_used_at ? formatDate(token.last_used_at) : t("tokens.never")}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <TokenStatus token={token} />
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm">
                    {!token.is_revoked && (
                      <button
                        onClick={() => handleRevoke(token.id, token.name)}
                        className="text-red-600 hover:text-red-800"
                      >
                        {t("tokens.revoke")}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

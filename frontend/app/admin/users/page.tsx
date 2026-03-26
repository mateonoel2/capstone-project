"use client";

import { useState } from "react";
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from "@/lib/hooks";
import { useExtractionStore } from "@/lib/store";
import { useRouter } from "next/navigation";
import { useT } from "@/lib/i18n";

export default function AdminUsersPage() {
  const router = useRouter();
  const backendUser = useExtractionStore((s) => s.backendUser);
  const { data: users, isLoading, error } = useUsers();
  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();
  const deleteUserMutation = useDeleteUser();
  const t = useT();

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newRole, setNewRole] = useState("user");

  // Redirect non-admins
  if (backendUser && backendUser.role !== "admin") {
    router.push("/");
    return null;
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername.trim()) return;
    try {
      await createUserMutation.mutateAsync({ github_username: newUsername.trim(), role: newRole });
      setNewUsername("");
      setNewRole("user");
      setShowCreateForm(false);
    } catch {
      // error is shown via mutation state
    }
  };

  const handleToggleActive = async (userId: string, currentActive: boolean) => {
    await updateUserMutation.mutateAsync({ id: userId, data: { is_active: !currentActive } });
  };

  const handleChangeRole = async (userId: string, newRole: string) => {
    await updateUserMutation.mutateAsync({ id: userId, data: { role: newRole } });
  };

  const handleDelete = async (userId: string, username: string) => {
    if (!confirm(t("admin.confirmDelete", { username }))) return;
    await deleteUserMutation.mutateAsync(userId);
  };

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t("admin.title")}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t("admin.subtitle")}
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          {t("admin.createUser")}
        </button>
      </div>

      {createUserMutation.error && (
        <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
          {createUserMutation.error.message}
        </div>
      )}

      {showCreateForm && (
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="mb-3 text-sm font-medium text-gray-900">{t("admin.newUser")}</h3>
          <form onSubmit={handleCreate} className="flex items-end gap-3">
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700">
                {t("admin.githubUsername")}
              </label>
              <input
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                placeholder="username"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700">{t("admin.role")}</label>
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
              >
                <option value="user">{t("admin.roleUser")}</option>
                <option value="admin">{t("admin.roleAdmin")}</option>
                <option value="guest">{t("admin.roleGuest")}</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={createUserMutation.isPending}
              className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
            >
              {createUserMutation.isPending ? t("admin.creating") : t("admin.create")}
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              {t("admin.cancel")}
            </button>
          </form>
        </div>
      )}

      {isLoading && <p className="text-sm text-gray-500">{t("admin.loadingUsers")}</p>}
      {error && <p className="text-sm text-red-600">{t("admin.loadError")}</p>}

      {users && (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("admin.userColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("admin.emailColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("admin.roleColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("admin.statusColumn")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  {t("admin.actionsColumn")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="whitespace-nowrap px-6 py-4">
                    <div className="flex items-center gap-3">
                      {user.avatar_url && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={user.avatar_url}
                          alt={user.github_username}
                          className="h-8 w-8 rounded-full"
                        />
                      )}
                      <span className="text-sm font-medium text-gray-900">
                        {user.github_username}
                      </span>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {user.email || "—"}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <select
                      value={user.role}
                      onChange={(e) => handleChangeRole(user.id, e.target.value)}
                      disabled={user.id === backendUser?.id}
                      className="rounded border border-gray-300 px-2 py-1 text-xs disabled:opacity-50"
                    >
                      <option value="user">{t("admin.roleUser")}</option>
                      <option value="admin">{t("admin.roleAdmin")}</option>
                      <option value="guest">{t("admin.roleGuest")}</option>
                    </select>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <button
                      onClick={() => handleToggleActive(user.id, user.is_active)}
                      disabled={user.id === backendUser?.id}
                      className="disabled:opacity-50"
                    >
                      <span
                        className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                          user.is_active
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {user.is_active ? t("admin.active") : t("admin.inactive")}
                      </span>
                    </button>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm">
                    {user.id !== backendUser?.id && (
                      <button
                        onClick={() => handleDelete(user.id, user.github_username)}
                        className="text-red-600 hover:text-red-800"
                      >
                        {t("admin.deleteUser")}
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

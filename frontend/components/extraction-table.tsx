"use client";

import { useState, useMemo } from "react";
import { ExtractionLog } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Search, AlertCircle, CheckCircle } from "lucide-react";

interface ExtractionTableProps {
  logs: ExtractionLog[];
}

export function ExtractionTable({ logs }: ExtractionTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<keyof ExtractionLog>("timestamp");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const filteredAndSortedLogs = useMemo(() => {
    let filtered = logs.filter((log) =>
      log.filename.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];

      if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
      if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [logs, searchTerm, sortField, sortDirection]);

  const handleSort = (field: keyof ExtractionLog) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const CorrectionBadge = ({ corrected }: { corrected: boolean }) => {
    if (corrected) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
          <AlertCircle className="h-3 w-3" />
          Corrected
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3" />
        Accurate
      </span>
    );
  };

  if (logs.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No extractions yet. Upload a PDF to get started!
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="text"
          placeholder="Search by filename..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="overflow-x-auto border rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th
                className="px-4 py-3 text-left font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("filename")}
              >
                Filename
              </th>
              <th
                className="px-4 py-3 text-left font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort("timestamp")}
              >
                Date
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">
                Owner
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">
                Bank Name
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">
                Account Number
              </th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredAndSortedLogs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-900">{log.filename}</td>
                <td className="px-4 py-3 text-gray-600">
                  {formatDate(log.timestamp)}
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    <div className="text-gray-900">{log.final_owner}</div>
                    <CorrectionBadge corrected={log.owner_corrected} />
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    <div className="text-gray-900">{log.final_bank_name}</div>
                    <CorrectionBadge corrected={log.bank_name_corrected} />
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    <div className="text-gray-900">
                      {log.final_account_number}
                    </div>
                    <CorrectionBadge corrected={log.account_number_corrected} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-sm text-gray-600">
        Showing {filteredAndSortedLogs.length} of {logs.length} extractions
      </div>
    </div>
  );
}


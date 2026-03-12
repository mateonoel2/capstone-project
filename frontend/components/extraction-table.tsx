"use client";

import { useState, useMemo } from "react";
import { ExtractionLog, PaginationMeta } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, AlertCircle, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";

interface ExtractionTableProps {
  logs: ExtractionLog[];
  pagination: PaginationMeta;
  onPageChange: (page: number) => void;
}

export function ExtractionTable({ logs, pagination, onPageChange }: ExtractionTableProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredLogs = useMemo(() => {
    return logs.filter((log) =>
      log.filename.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [logs, searchTerm]);

  const fieldKeys = useMemo(() => {
    const keys = new Set<string>();
    for (const log of logs) {
      for (const key of Object.keys(log.final_fields || {})) {
        keys.add(key);
      }
      for (const key of Object.keys(log.extracted_fields || {})) {
        keys.add(key);
      }
    }
    return Array.from(keys);
  }, [logs]);

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

  const formatFieldName = (field: string) => {
    return field.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const CorrectionBadge = ({ corrected }: { corrected: boolean }) => {
    if (corrected) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
          <AlertCircle className="h-3 w-3" />
          Corregido
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3" />
        Preciso
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
              <th className="px-4 py-3 text-left font-medium text-gray-700">
                Filename
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">
                Date
              </th>
              {fieldKeys.map((field) => (
                <th key={field} className="px-4 py-3 text-left font-medium text-gray-700">
                  {formatFieldName(field)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredLogs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-900">{log.filename}</td>
                <td className="px-4 py-3 text-gray-600">
                  {formatDate(log.timestamp)}
                </td>
                {fieldKeys.map((field) => (
                  <td key={field} className="px-4 py-3">
                    <div className="space-y-1">
                      <div className="text-gray-900">{(log.final_fields || {})[field] ?? ""}</div>
                      <CorrectionBadge corrected={(log.corrected_fields || {})[field] ?? false} />
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing {((pagination.page - 1) * pagination.page_size) + 1} to {Math.min(pagination.page * pagination.page_size, pagination.total)} of {pagination.total} extractions
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

      <div className="text-sm text-gray-600">
            Page {pagination.page} of {pagination.total_pages}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.total_pages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

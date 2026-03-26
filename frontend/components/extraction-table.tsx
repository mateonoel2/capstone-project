"use client";

import { useState, useMemo } from "react";
import { ExtractionLog, PaginationMeta } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, AlertCircle, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { useT } from "@/lib/i18n";

interface ExtractionTableProps {
  logs: ExtractionLog[];
  pagination: PaginationMeta;
  onPageChange: (page: number) => void;
  showExtractor?: boolean;
}

export function ExtractionTable({ logs, pagination, onPageChange, showExtractor = false }: ExtractionTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const t = useT();

  const filteredLogs = useMemo(() => {
    return logs.filter((log) =>
      log.filename.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [logs, searchTerm]);

  const fieldKeys = useMemo(() => {
    if (showExtractor) return [];
    const keys = new Set<string>();
    for (const log of logs) {
      for (const key of Object.keys(log.final_fields || {})) keys.add(key);
      for (const key of Object.keys(log.extracted_fields || {})) keys.add(key);
    }
    return Array.from(keys);
  }, [logs, showExtractor]);

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

  const formatValue = (value: unknown): string => {
    if (value == null) return "";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  };

  const CorrectionBadge = ({ corrected }: { corrected: boolean }) => {
    if (corrected) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
          <AlertCircle className="h-3 w-3" />
          {t("extractionTable.corrected")}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3" />
        {t("extractionTable.accurate")}
      </span>
    );
  };

  if (logs.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        {t("extractionTable.noExtractions")}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="text"
          placeholder={t("extractionTable.searchPlaceholder")}
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
                {t("extractionTable.filename")}
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">
                {t("extractionTable.date")}
              </th>
              {showExtractor ? (
                <>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">
                    {t("extractionTable.extractor")}
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">
                    {t("extractionTable.fields")}
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">
                    {t("extractionTable.status")}
                  </th>
                </>
              ) : (
                fieldKeys.map((field) => (
                  <th key={field} className="px-4 py-3 text-left font-medium text-gray-700">
                    {formatFieldName(field)}
                  </th>
                ))
              )}
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredLogs.map((log) => {
              const corrected = log.corrected_fields || {};
              const totalFields = Object.keys(corrected).length;
              const correctedCount = Object.values(corrected).filter(Boolean).length;
              const allAccurate = correctedCount === 0;

              return (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900 font-medium max-w-xs truncate">
                    {log.filename}
                  </td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                    {formatDate(log.timestamp)}
                  </td>
                  {showExtractor ? (
                    <>
                      <td className="px-4 py-3 text-gray-600">
                        {log.extractor_config_name ?? "—"}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {totalFields}
                      </td>
                      <td className="px-4 py-3">
                        {allAccurate ? (
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3" />
                            {t("extractionTable.accurate")}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                            <AlertCircle className="h-3 w-3" />
                            {t("extractionTable.correctedCount", {
                              count: String(correctedCount),
                              total: String(totalFields),
                            })}
                          </span>
                        )}
                      </td>
                    </>
                  ) : (
                    fieldKeys.map((field) => (
                      <td key={field} className="px-4 py-3">
                        <div className="space-y-1">
                          <div className="text-gray-900">
                            {formatValue((log.final_fields || {})[field])}
                          </div>
                          <CorrectionBadge corrected={(corrected)[field] ?? false} />
                        </div>
                      </td>
                    ))
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {t("extractionTable.showing", {
            from: String(((pagination.page - 1) * pagination.page_size) + 1),
            to: String(Math.min(pagination.page * pagination.page_size, pagination.total)),
            total: String(pagination.total),
          })}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
            {t("extractionTable.previous")}
          </Button>

          <div className="text-sm text-gray-600">
            {t("extractionTable.page", {
              current: String(pagination.page),
              total: String(pagination.total_pages),
            })}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.total_pages}
          >
            {t("extractionTable.next")}
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

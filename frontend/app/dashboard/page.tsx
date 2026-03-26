"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { ExtractionTable } from "@/components/extraction-table";
import { useMetrics, useApiCallMetrics, useExtractionLogs, useExtractorConfigs } from "@/lib/hooks";
import { BarChart3, TrendingUp, FileCheck, AlertCircle, Loader2, Zap, Activity, Clock } from "lucide-react";
import { useT } from "@/lib/i18n";

export default function Dashboard() {
  const [selectedConfigId, setSelectedConfigId] = useState<string>("all");
  const [page, setPage] = useState(1);
  const t = useT();

  const configIdParam = useMemo(
    () => selectedConfigId === "all" ? undefined : Number(selectedConfigId),
    [selectedConfigId]
  );

  const { data: extractorConfigs = [] } = useExtractorConfigs("active");
  const { data: metrics, isLoading: metricsLoading } = useMetrics(configIdParam);
  const { data: apiMetrics } = useApiCallMetrics(configIdParam);
  const { data: logsData, isLoading: logsLoading } = useExtractionLogs(page, 50, configIdParam);

  const logs = logsData?.logs ?? [];
  const pagination = logsData?.pagination ?? { total: 0, page: 1, page_size: 50, total_pages: 0 };
  const isLoading = metricsLoading && logsLoading;

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleConfigChange = (value: string) => {
    setSelectedConfigId(value);
    setPage(1);
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-600">{t("dashboard.loading")}</span>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t("dashboard.title")}</h1>
            <p className="text-gray-600 mt-1">
              {t("dashboard.subtitle")}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="config-filter" className="text-sm whitespace-nowrap">
              {t("dashboard.filterByExtractor")}
            </Label>
            <Select value={selectedConfigId} onValueChange={handleConfigChange}>
              <SelectTrigger id="config-filter" className="w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("dashboard.allExtractors")}</SelectItem>
                {extractorConfigs.map((config) => (
                  <SelectItem key={config.id} value={config.id.toString()}>
                    {config.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {t("dashboard.totalExtractions")}
              </CardTitle>
              <FileCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.total_extractions || 0}</div>
              <p className="text-xs text-muted-foreground">
                {t("dashboard.historicalTotal")}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {t("dashboard.correctionsTitle")}
              </CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.total_corrections || 0}</div>
              <p className="text-xs text-muted-foreground">
                {t("dashboard.correctionsDesc")}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {t("dashboard.accuracyRate")}
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.accuracy_rate || 0}%</div>
              <p className="text-xs text-muted-foreground">
                {t("dashboard.accuracyDesc")}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {t("dashboard.thisWeek")}
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.this_week || 0}</div>
              <p className="text-xs text-muted-foreground">
                {t("dashboard.last7days")}
              </p>
            </CardContent>
          </Card>
        </div>

        {selectedConfigId !== "all" && metrics?.field_accuracies && Object.keys(metrics.field_accuracies).length > 0 && (
          <div className={`grid grid-cols-1 ${{1: "md:grid-cols-1", 2: "md:grid-cols-2", 3: "md:grid-cols-3", 4: "md:grid-cols-4"}[Math.min(Object.keys(metrics.field_accuracies).length, 4)] ?? "md:grid-cols-4"} gap-6 mb-8`}>
            {Object.entries(metrics.field_accuracies).map(([field, accuracy], idx) => {
              const colors = ["text-blue-500", "text-green-500", "text-purple-500", "text-orange-500", "text-pink-500"];
              const color = colors[idx % colors.length];
              return (
                <Card key={field} className="flex flex-col items-center justify-center p-6">
                  <div className="relative w-32 h-32 mb-4">
                    <svg className="transform -rotate-90 w-32 h-32">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 56}`}
                        strokeDashoffset={`${2 * Math.PI * 56 * (1 - (accuracy || 0) / 100)}`}
                        className={`${color} transition-all duration-1000 ease-out`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold text-gray-900">{accuracy || 0}%</span>
                    </div>
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900">{field.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</h3>
                  <p className="text-xs text-gray-500 mt-1">{t("dashboard.fieldAccuracyRate")}</p>
                </Card>
              );
            })}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t("dashboard.apiCalls")}</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{apiMetrics?.total_calls || 0}</div>
              <p className="text-xs text-muted-foreground">
                {t("dashboard.apiCallsThisWeek", { count: String(apiMetrics?.calls_this_week || 0) })}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t("dashboard.errorRate")}</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{apiMetrics?.error_rate || 0}%</div>
              <p className="text-xs text-muted-foreground">
                {t("dashboard.failures", { count: String(apiMetrics?.total_failures || 0) })}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t("dashboard.avgResponseTime")}</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {apiMetrics?.avg_response_time_ms
                  ? (apiMetrics.avg_response_time_ms / 1000).toFixed(1)
                  : "0"}s
              </div>
              <p className="text-xs text-muted-foreground">{t("dashboard.apiLatency")}</p>
            </CardContent>
          </Card>
        </div>

        {apiMetrics && apiMetrics.error_breakdown.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-sm font-medium">{t("dashboard.errorBreakdown")}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {apiMetrics.error_breakdown.map((item) => (
                  <div key={item.error_type} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{item.error_type}</span>
                    <span className="font-medium">{item.count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.recentExtractions")}</CardTitle>
            <CardDescription>
              {t("dashboard.recentExtractionsDesc")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExtractionTable
              logs={logs}
              pagination={pagination}
              onPageChange={handlePageChange}
              showExtractor={selectedConfigId === "all"}
            />
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

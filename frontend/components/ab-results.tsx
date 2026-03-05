"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ABTestResultItem } from "@/lib/api";
import { AlertCircle, Clock } from "lucide-react";

interface ABResultsProps {
  results: ABTestResultItem[];
}

export function ABResults({ results }: ABResultsProps) {
  // Collect all field keys across all results
  const allKeys = new Set<string>();
  results.forEach((r) => {
    if (r.fields) Object.keys(r.fields).forEach((k) => allKeys.add(k));
  });

  // For each key, check if all results agree
  const fieldValues: Record<string, string[]> = {};
  for (const key of allKeys) {
    fieldValues[key] = results.map((r) =>
      r.fields ? String(r.fields[key] ?? "") : ""
    );
  }

  const allSame = (values: string[]) =>
    values.every((v) => v === values[0]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {results.map((result, idx) => (
        <Card
          key={idx}
          className={!result.success ? "border-red-200 bg-red-50/50" : ""}
        >
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">
                {result.parser_config_name}
              </CardTitle>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="h-3 w-3" />
                {(result.response_time_ms / 1000).toFixed(1)}s
              </div>
            </div>
            <CardDescription className="text-xs">
              Modelo: {result.model}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!result.success ? (
              <div className="flex items-start gap-2 text-red-600">
                <AlertCircle className="h-4 w-4 mt-0.5" />
                <p className="text-sm">{result.error}</p>
              </div>
            ) : (
              <div className="space-y-2">
                {Array.from(allKeys).map((key) => {
                  const value = String(result.fields[key] ?? "");
                  const values = fieldValues[key];
                  const matches = allSame(values);

                  return (
                    <div key={key}>
                      <p className="text-xs font-medium text-gray-500 capitalize">
                        {key.replace(/_/g, " ")}
                      </p>
                      <p
                        className={`text-sm ${
                          matches
                            ? "text-green-700 bg-green-50"
                            : "text-yellow-700 bg-yellow-50"
                        } px-2 py-1 rounded`}
                      >
                        {value || "(vacío)"}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

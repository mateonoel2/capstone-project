"use client";

import { useState, useEffect } from "react";
import { FileUpload } from "@/components/file-upload";
import { FileViewer } from "@/components/file-viewer";
import { BankCombobox } from "@/components/bank-combobox";
import { DynamicFieldsForm } from "@/components/dynamic-fields-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toStr } from "@/lib/utils";
import { useExtractionStore } from "@/lib/store";
import { useBanks, useExtractorConfigs, useUploadFile, useExtract, useSubmitExtraction, useUsageQuota } from "@/lib/hooks";
import { Loader2, CheckCircle, AlertCircle, Info } from "lucide-react";
import { useT } from "@/lib/i18n";

export default function Home() {
  const {
    file,
    uploadResult,
    extracted,
    formData,
    selectedExtractorId,
    setFile,
    setUploadResult,
    setExtracted,
    updateFormField,
    setFormData,
    setSelectedExtractorId,
    reset: resetStore,
  } = useExtractionStore();

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const t = useT();

  const { data: banks = [] } = useBanks();
  const { data: extractorConfigs = [] } = useExtractorConfigs("active");
  const { data: quota } = useUsageQuota();

  const extractionLimitReached = !!(
    quota &&
    !quota.unlimited &&
    quota.extractions &&
    quota.extractions.used >= quota.extractions.limit
  );

  const uploadFile = useUploadFile();
  const extract = useExtract();
  const submitMutation = useSubmitExtraction();

  useEffect(() => {
    if (!selectedExtractorId && extractorConfigs.length > 0) {
      const defaultConfig = extractorConfigs.find((c) => c.is_default);
      if (defaultConfig) setSelectedExtractorId(defaultConfig.id);
    }
  }, [extractorConfigs, selectedExtractorId, setSelectedExtractorId]);

  const selectedConfig = extractorConfigs.find((c) => c.id === selectedExtractorId);
  const isBankStatementExtractor =
    (selectedConfig?.is_default ?? true) &&
    !!(selectedConfig?.output_schema as Record<string, unknown> | undefined)?.properties &&
    "account_number" in
      ((selectedConfig?.output_schema as Record<string, Record<string, unknown>>)?.properties ?? {});

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setSuccess(false);
    setUploadResult(null);
    setExtracted(null);
    setFormData({});

    uploadFile.mutate(selectedFile, {
      onSuccess: (result) => {
        setUploadResult(result);
      },
      onError: (err) => {
        setError(err instanceof Error ? err.message : t("extraction.extractionFailed"));
      },
    });
  };

  const handleExtract = () => {
    if (!uploadResult) return;
    setError(null);

    extract.mutate(
      {
        s3Key: uploadResult.s3_key,
        filename: uploadResult.filename,
        extractorConfigId: selectedExtractorId,
      },
      {
        onSuccess: (result) => {
          setExtracted(result);
          const fields: Record<string, string> = {};
          for (const [key, value] of Object.entries(result.fields || {})) {
            fields[key] = toStr(value);
          }
          setFormData(fields);
        },
        onError: (err) => {
          setError(err instanceof Error ? err.message : t("extraction.extractionFailed"));
          setExtracted(null);
        },
      }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !extracted) return;

    setError(null);

    const extractedFields: Record<string, string> = {};
    for (const [key, value] of Object.entries(extracted.fields || {})) {
      extractedFields[key] = toStr(value);
    }

    submitMutation.mutate(
      {
        filename: file.name,
        extracted_fields: extractedFields,
        final_fields: formData,
        extractor_config_id: selectedExtractorId,
        extractor_config_version_id: extracted.extractor_config_version_id,
      },
      {
        onSuccess: () => {
          setSuccess(true);
          setTimeout(() => {
            resetStore();
            setSuccess(false);
          }, 2000);
        },
        onError: (err) => {
          setError(err instanceof Error ? err.message : t("extraction.submissionFailed"));
        },
      }
    );
  };

  const handleReset = () => {
    resetStore();
    setError(null);
    setSuccess(false);
  };

  const isModified =
    extracted &&
    Object.entries(formData).some(
      ([key, value]) => value !== toStr(extracted.fields?.[key])
    );

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            {t("extraction.title")}
          </h1>
          <p className="text-gray-600 mt-1">
            {t("extraction.subtitle")}
          </p>
        </div>

        <div className="mb-4 flex items-start gap-2 rounded-lg bg-blue-50 border border-blue-200 px-4 py-3 text-sm text-blue-800">
          <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <p>
            {t("extraction.apiNote")}{" "}
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium underline hover:text-blue-900"
            >
              {t("extraction.apiDocsLink")}
            </a>
            {t("extraction.apiNoteSuffix")}
          </p>
        </div>

        <div className="mb-4">
          <Label htmlFor="extractor-select" className="text-sm font-medium">
            {t("extraction.extractor")}
          </Label>
          <Select
            value={selectedExtractorId?.toString() ?? ""}
            onValueChange={(v) => {
              if (file && !window.confirm(t("extraction.confirmChangeExtractor"))) return;
              resetStore();
              setSelectedExtractorId(v);
              setError(null);
              setSuccess(false);
            }}
          >
            <SelectTrigger id="extractor-select" className="w-80 mt-1">
              <SelectValue placeholder={t("extraction.selectExtractor")} />
            </SelectTrigger>
            <SelectContent>
              {extractorConfigs.map((config) => (
                <SelectItem key={config.id} value={config.id.toString()}>
                  {config.name}
                  {config.is_default ? ` ${t("extraction.default")}` : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedConfig && (() => {
            const schema = selectedConfig.output_schema as { properties?: Record<string, { type?: string; description?: string }>; required?: string[] };
            const properties = schema?.properties || {};
            const required = new Set(schema?.required || []);
            const fieldNames = Object.keys(properties).filter((k) => k !== "is_valid_document");
            if (fieldNames.length === 0) return null;
            return (
              <div className="mt-3 rounded-lg border border-gray-200 bg-white p-3">
                {selectedConfig.description && (
                  <p className="text-sm text-gray-600 mb-2">{selectedConfig.description}</p>
                )}
                <p className="text-xs font-medium text-gray-500 mb-2">{t("extraction.fieldsToExtract")}</p>
                <div className="flex flex-wrap gap-1.5">
                  {fieldNames.map((field) => (
                    <span
                      key={field}
                      className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 text-xs text-gray-700"
                      title={properties[field]?.description || ""}
                    >
                      {field.replace(/_/g, " ")}
                      {required.has(field) && (
                        <span className="text-[10px] text-blue-600 font-medium">
                          ({t("extraction.requiredField")})
                        </span>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            );
          })()}
        </div>

        {!file ? (
          <>
            {extractionLimitReached && (
              <div className="mb-4 flex items-start gap-2 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>{t("quota.limitReached")}</p>
              </div>
            )}
            <FileUpload
              onFileSelect={extractionLimitReached ? () => {} : handleFileSelect}
              isLoading={uploadFile.isPending}
            />
          </>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>{t("extraction.document")}</CardTitle>
                  <CardDescription>{file.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[600px]">
                    <FileViewer file={file} />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>{t("extraction.extractedInfo")}</CardTitle>
                  <CardDescription>
                    {isBankStatementExtractor
                      ? t("extraction.reviewDefault")
                      : `${t("extraction.extractor")}: ${selectedConfig?.name}`}
                    {extracted?.extractor_config_version_number != null && (
                      <span className="ml-2 text-xs font-medium text-blue-700 bg-blue-100 px-1.5 py-0.5 rounded">
                        {t("extraction.version", { number: String(extracted.extractor_config_version_number) })}
                      </span>
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {uploadFile.isPending ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                      <span className="ml-2 text-gray-600">
                        {t("extraction.uploading")}
                      </span>
                    </div>
                  ) : extract.isPending ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                      <span className="ml-2 text-gray-600">
                        {t("extraction.extracting")}
                      </span>
                    </div>
                  ) : !extracted && uploadResult ? (
                    <div className="space-y-4 py-6 text-center">
                      <p className="text-sm text-gray-600">
                        {t("extraction.readyToExtract")}
                      </p>
                      {error && (
                        <div className="flex items-start gap-3 text-red-600 bg-red-50 p-4 rounded-lg text-left">
                          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="font-medium">{t("extraction.extractionError")}</p>
                            <p className="text-sm mt-1">{error}</p>
                          </div>
                        </div>
                      )}
                      <Button onClick={handleExtract} className="w-full">
                        {t("extraction.extract")}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={handleReset}
                        className="w-full"
                      >
                        {t("extraction.reset")}
                      </Button>
                    </div>
                  ) : error && !extracted ? (
                    <div className="space-y-4 py-6">
                      <div className="flex items-start gap-3 text-red-600 bg-red-50 p-4 rounded-lg">
                        <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-medium">{t("extraction.extractionError")}</p>
                          <p className="text-sm mt-1">{error}</p>
                        </div>
                      </div>
                      <Button
                        onClick={handleReset}
                        variant="outline"
                        className="w-full"
                      >
                        {t("extraction.tryAnother")}
                      </Button>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-4">
                      {isBankStatementExtractor ? (
                        <>
                          <div className="space-y-2">
                            <Label htmlFor="owner">{t("extraction.owner")}</Label>
                            <Input
                              id="owner"
                              value={formData.owner || ""}
                              onChange={(e) =>
                                updateFormField("owner", e.target.value)
                              }
                              placeholder={t("extraction.ownerPlaceholder")}
                              className={
                                extracted && formData.owner !== toStr(extracted.fields?.owner)
                                  ? "border-yellow-400"
                                  : ""
                              }
                            />
                            {extracted && formData.owner !== toStr(extracted.fields?.owner) && (
                              <p className="text-xs text-yellow-600">
                                {t("extraction.aiExtracted", { value: toStr(extracted.fields?.owner) || t("extraction.empty") })}
                              </p>
                            )}
                          </div>

                          <div className="space-y-2">
                            <Label htmlFor="bank_name">{t("extraction.bank")}</Label>
                            <BankCombobox
                              banks={banks}
                              value={formData.bank_name || ""}
                              onChange={(value) =>
                                updateFormField("bank_name", value)
                              }
                              className={
                                extracted &&
                                formData.bank_name !== toStr(extracted.fields?.bank_name)
                                  ? "border-yellow-400"
                                  : ""
                              }
                            />
                            {extracted &&
                              formData.bank_name !== toStr(extracted.fields?.bank_name) && (
                                <p className="text-xs text-yellow-600">
                                  {t("extraction.aiExtracted", { value: toStr(extracted.fields?.bank_name) || t("extraction.empty") })}
                                </p>
                              )}
                          </div>

                          <div className="space-y-2">
                            <Label htmlFor="account_number">
                              {t("extraction.accountNumber")}
                            </Label>
                            <Input
                              id="account_number"
                              value={formData.account_number || ""}
                              onChange={(e) =>
                                updateFormField("account_number", e.target.value)
                              }
                              placeholder={t("extraction.accountPlaceholder")}
                              className={
                                extracted &&
                                formData.account_number !==
                                  toStr(extracted.fields?.account_number)
                                  ? "border-yellow-400"
                                  : ""
                              }
                            />
                            {extracted &&
                              formData.account_number !==
                                toStr(extracted.fields?.account_number) && (
                                <p className="text-xs text-yellow-600">
                                  {t("extraction.aiExtracted", { value: toStr(extracted.fields?.account_number) || t("extraction.empty") })}
                                </p>
                              )}
                          </div>
                        </>
                      ) : (
                        <DynamicFieldsForm
                          schema={
                            selectedConfig?.output_schema as Record<
                              string,
                              unknown
                            >
                          }
                          values={formData}
                          extracted={extracted?.fields as Record<string, unknown>}
                          onChange={updateFormField}
                        />
                      )}

                      {error && (
                        <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded">
                          <AlertCircle className="h-4 w-4" />
                          <span className="text-sm">{error}</span>
                        </div>
                      )}

                      {success && (
                        <div className="flex items-center gap-2 text-green-600 bg-green-50 p-3 rounded">
                          <CheckCircle className="h-4 w-4" />
                          <span className="text-sm">
                            {t("extraction.submittedSuccess")}
                          </span>
                        </div>
                      )}

                      {isModified && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                          <p className="text-sm text-yellow-800">
                            {t("extraction.modifiedWarning")}
                          </p>
                        </div>
                      )}

                      <div className="flex gap-2 pt-4">
                        <Button
                          type="submit"
                          disabled={submitMutation.isPending || success}
                          className="flex-1"
                        >
                          {submitMutation.isPending ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              {t("extraction.submitting")}
                            </>
                          ) : (
                            t("extraction.submit")
                          )}
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={handleReset}
                          disabled={submitMutation.isPending}
                        >
                          {t("extraction.reset")}
                        </Button>
                      </div>
                    </form>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

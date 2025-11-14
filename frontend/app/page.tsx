"use client";

import { useState, useEffect } from "react";
import { FileUpload } from "@/components/file-upload";
import { PDFViewer } from "@/components/pdf-viewer";
import { BankCombobox } from "@/components/bank-combobox";
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
import { extractFromPDF, submitExtraction, getBanks, Bank } from "@/lib/api";
import { useExtractionStore } from "@/lib/store";
import { Loader2, CheckCircle, AlertCircle } from "lucide-react";

export default function Home() {
  const {
    file,
    extracted,
    formData,
    setFile,
    setExtracted,
    updateFormField,
    setFormData,
    reset: resetStore,
  } = useExtractionStore();

  const [isExtracting, setIsExtracting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [banks, setBanks] = useState<Bank[]>([]);

  useEffect(() => {
    const fetchBanks = async () => {
      try {
        const bankList = await getBanks();
        setBanks(bankList);
      } catch (err) {
        console.error("Failed to fetch banks:", err);
      }
    };
    fetchBanks();
  }, []);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setSuccess(false);
    setIsExtracting(true);

    try {
      const result = await extractFromPDF(selectedFile);
      setExtracted(result);
      setFormData({
        owner: result.owner,
        bank_name: result.bank_name,
        account_number: result.account_number,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Extraction failed");
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !extracted) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await submitExtraction({
        filename: file.name,
        extracted_owner: extracted.owner,
        extracted_bank_name: extracted.bank_name,
        extracted_account_number: extracted.account_number,
        final_owner: formData.owner,
        final_bank_name: formData.bank_name,
        final_account_number: formData.account_number,
      });
      setSuccess(true);
      setTimeout(() => {
        resetStore();
        setSuccess(false);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    resetStore();
    setError(null);
    setSuccess(false);
  };

  const isModified =
    extracted &&
    (formData.owner !== extracted.owner ||
      formData.bank_name !== extracted.bank_name ||
      formData.account_number !== extracted.account_number);

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Bank Statement Extraction
          </h1>
          <p className="text-gray-600 mt-1">
            Upload a PDF bank statement to extract and verify account
            information
          </p>
        </div>

        {!file ? (
          <FileUpload
            onFileSelect={handleFileSelect}
            isLoading={isExtracting}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>PDF Document</CardTitle>
                  <CardDescription>{file.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[600px]">
                    <PDFViewer file={file} />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Extracted Information</CardTitle>
                  <CardDescription>
                    Review and correct the extracted data before submitting
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isExtracting ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                      <span className="ml-2 text-gray-600">
                        Extracting data...
                      </span>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="owner">Account Owner</Label>
                        <Input
                          id="owner"
                          value={formData.owner}
                          onChange={(e) =>
                            updateFormField("owner", e.target.value)
                          }
                          placeholder="Enter account owner name"
                          className={
                            extracted && formData.owner !== extracted.owner
                              ? "border-yellow-400"
                              : ""
                          }
                        />
                        {extracted && formData.owner !== extracted.owner && (
                          <p className="text-xs text-yellow-600">
                            AI extracted: {extracted.owner || "(empty)"}
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="bank_name">Bank Name</Label>
                        <BankCombobox
                          banks={banks}
                          value={formData.bank_name}
                          onChange={(value) =>
                            updateFormField("bank_name", value)
                          }
                          className={
                            extracted &&
                            formData.bank_name !== extracted.bank_name
                              ? "border-yellow-400"
                              : ""
                          }
                        />
                        {extracted &&
                          formData.bank_name !== extracted.bank_name && (
                            <p className="text-xs text-yellow-600">
                              AI extracted: {extracted.bank_name || "(empty)"}
                            </p>
                          )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="account_number">Account Number</Label>
                        <Input
                          id="account_number"
                          value={formData.account_number}
                          onChange={(e) =>
                            updateFormField("account_number", e.target.value)
                          }
                          placeholder="Enter account number"
                          className={
                            extracted &&
                            formData.account_number !== extracted.account_number
                              ? "border-yellow-400"
                              : ""
                          }
                        />
                        {extracted &&
                          formData.account_number !==
                            extracted.account_number && (
                            <p className="text-xs text-yellow-600">
                              AI extracted: {extracted.account_number || "(empty)"}
                            </p>
                          )}
                      </div>

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
                            Submitted successfully!
                          </span>
                        </div>
                      )}

                      {isModified && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                          <p className="text-sm text-yellow-800">
                            You have made changes to the extracted data
                          </p>
                        </div>
                      )}

                      <div className="flex gap-2 pt-4">
                        <Button
                          type="submit"
                          disabled={isSubmitting || success}
                          className="flex-1"
                        >
                          {isSubmitting ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Submitting...
                            </>
                          ) : (
                            "Submit"
                          )}
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={handleReset}
                          disabled={isSubmitting}
                        >
                          Reset
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

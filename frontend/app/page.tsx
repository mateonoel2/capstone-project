"use client";

import { useState, useEffect } from "react";
import { FileUpload } from "@/components/file-upload";
import { FileViewer } from "@/components/file-viewer";
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
import { extractFromFile, submitExtraction, getBanks, Bank } from "@/lib/api";
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
      const result = await extractFromFile(selectedFile);
      setExtracted(result);
      setFormData({
        owner: result.owner,
        bank_name: result.bank_name,
        account_number: result.account_number,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "La extracción falló");
      setExtracted(null);
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
      setError(err instanceof Error ? err.message : "El envío falló");
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
            Extracción de Estados de Cuenta
          </h1>
          <p className="text-gray-600 mt-1">
            Sube un estado de cuenta bancario (PDF o imagen) para extraer y
            verificar la información de la cuenta
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
                  <CardTitle>Documento</CardTitle>
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
                  <CardTitle>Información Extraída</CardTitle>
                  <CardDescription>
                    Revisa y corrige los datos extraídos antes de enviar
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isExtracting ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                      <span className="ml-2 text-gray-600">
                        Extrayendo datos...
                      </span>
                    </div>
                  ) : error && !extracted ? (
                    <div className="space-y-4 py-6">
                      <div className="flex items-start gap-3 text-red-600 bg-red-50 p-4 rounded-lg">
                        <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-medium">Error en la extracción</p>
                          <p className="text-sm mt-1">{error}</p>
                        </div>
                      </div>
                      <Button
                        onClick={handleReset}
                        variant="outline"
                        className="w-full"
                      >
                        Intentar con otro archivo
                      </Button>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="owner">Titular de la Cuenta</Label>
                        <Input
                          id="owner"
                          value={formData.owner}
                          onChange={(e) =>
                            updateFormField("owner", e.target.value)
                          }
                          placeholder="Nombre del titular"
                          className={
                            extracted && formData.owner !== extracted.owner
                              ? "border-yellow-400"
                              : ""
                          }
                        />
                        {extracted && formData.owner !== extracted.owner && (
                          <p className="text-xs text-yellow-600">
                            IA extrajo: {extracted.owner || "(vacío)"}
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="bank_name">Banco</Label>
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
                              IA extrajo: {extracted.bank_name || "(vacío)"}
                            </p>
                          )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="account_number">Número de Cuenta (CLABE)</Label>
                        <Input
                          id="account_number"
                          value={formData.account_number}
                          onChange={(e) =>
                            updateFormField("account_number", e.target.value)
                          }
                          placeholder="CLABE de 18 dígitos"
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
                              IA extrajo: {extracted.account_number || "(vacío)"}
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
                            Enviado exitosamente!
                          </span>
                        </div>
                      )}

                      {isModified && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                          <p className="text-sm text-yellow-800">
                            Has modificado los datos extraídos
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
                              Enviando...
                            </>
                          ) : (
                            "Enviar"
                          )}
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={handleReset}
                          disabled={isSubmitting}
                        >
                          Reiniciar
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

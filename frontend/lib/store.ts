import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { ExtractionResult } from "./api";

interface AuthUser {
  id: string;
  github_username: string;
  email: string | null;
  avatar_url: string | null;
  role: string;
}

interface UploadResult {
  s3_key: string;
  filename: string;
}

interface ExtractionState {
  file: File | null;
  fileName: string | null;
  fileData: string | null;
  uploadResult: UploadResult | null;
  extracted: ExtractionResult | null;
  formData: Record<string, string>;
  selectedExtractorId: string | null;
  backendToken: string | null;
  backendUser: AuthUser | null;
  setFile: (file: File | null) => void;
  setUploadResult: (result: UploadResult | null) => void;
  setExtracted: (extracted: ExtractionResult | null) => void;
  setFormData: (formData: Record<string, string>) => void;
  updateFormField: (field: string, value: string) => void;
  setSelectedExtractorId: (id: string | null) => void;
  setBackendAuth: (token: string, user: AuthUser) => void;
  clearBackendAuth: () => void;
  reset: () => void;
}

const initialState = {
  file: null,
  fileName: null,
  fileData: null,
  uploadResult: null,
  extracted: null,
  formData: {} as Record<string, string>,
  selectedExtractorId: null as string | null,
  backendToken: null as string | null,
  backendUser: null as AuthUser | null,
};

export const useExtractionStore = create<ExtractionState>()(
  persist(
    (set) => ({
      ...initialState,

      setFile: (file) => {
        if (!file) {
          set({ file: null, fileName: null, fileData: null });
          return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
          set({
            file,
            fileName: file.name,
            fileData: reader.result as string,
          });
        };
        reader.readAsDataURL(file);
      },

      setUploadResult: (uploadResult) => set({ uploadResult }),

      setExtracted: (extracted) => set({ extracted }),

      setFormData: (formData) => set({ formData }),

      updateFormField: (field, value) =>
        set((state) => ({
          formData: {
            ...state.formData,
            [field]: value,
          },
        })),

      setSelectedExtractorId: (id) => set({ selectedExtractorId: id }),

      setBackendAuth: (token, user) => set({ backendToken: token, backendUser: user }),

      clearBackendAuth: () => set({ backendToken: null, backendUser: null }),

      reset: () =>
        set((state) => ({
          ...initialState,
          backendToken: state.backendToken,
          backendUser: state.backendUser,
          selectedExtractorId: state.selectedExtractorId,
        })),
    }),
    {
      name: "extraction-storage-v2",
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        fileName: state.fileName,
        uploadResult: state.uploadResult,
        extracted: state.extracted,
        formData: state.formData,
        selectedExtractorId: state.selectedExtractorId,
        backendToken: state.backendToken,
        backendUser: state.backendUser,
      }),
    }
  )
);

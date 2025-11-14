import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { ExtractionResult } from "./api";

interface ExtractionState {
  file: File | null;
  fileName: string | null;
  fileData: string | null;
  extracted: ExtractionResult | null;
  formData: {
    owner: string;
    bank_name: string;
    account_number: string;
  };
  setFile: (file: File | null) => void;
  setExtracted: (extracted: ExtractionResult | null) => void;
  setFormData: (formData: { owner: string; bank_name: string; account_number: string }) => void;
  updateFormField: (field: keyof ExtractionState["formData"], value: string) => void;
  reset: () => void;
}

const initialState = {
  file: null,
  fileName: null,
  fileData: null,
  extracted: null,
  formData: {
    owner: "",
    bank_name: "",
    account_number: "",
  },
};

export const useExtractionStore = create<ExtractionState>()(
  persist(
    (set, get) => ({
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

      setExtracted: (extracted) => set({ extracted }),

      setFormData: (formData) => set({ formData }),

      updateFormField: (field, value) =>
        set((state) => ({
          formData: {
            ...state.formData,
            [field]: value,
          },
        })),

      reset: () => set(initialState),
    }),
    {
      name: "extraction-storage",
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        fileName: state.fileName,
        extracted: state.extracted,
        formData: state.formData,
      }),
    }
  )
);


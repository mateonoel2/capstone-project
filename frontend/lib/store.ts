import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { ExtractionResult } from "./api";

interface ExtractionState {
  file: File | null;
  fileName: string | null;
  fileData: string | null;
  extracted: ExtractionResult | null;
  formData: Record<string, string>;
  selectedParserId: number | null;
  setFile: (file: File | null) => void;
  setExtracted: (extracted: ExtractionResult | null) => void;
  setFormData: (formData: Record<string, string>) => void;
  updateFormField: (field: string, value: string) => void;
  setSelectedParserId: (id: number | null) => void;
  reset: () => void;
}

const initialState = {
  file: null,
  fileName: null,
  fileData: null,
  extracted: null,
  formData: {} as Record<string, string>,
  selectedParserId: null as number | null,
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

      setExtracted: (extracted) => set({ extracted }),

      setFormData: (formData) => set({ formData }),

      updateFormField: (field, value) =>
        set((state) => ({
          formData: {
            ...state.formData,
            [field]: value,
          },
        })),

      setSelectedParserId: (id) => set({ selectedParserId: id }),

      reset: () => set(initialState),
    }),
    {
      name: "extraction-storage",
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        fileName: state.fileName,
        extracted: state.extracted,
        formData: state.formData,
        selectedParserId: state.selectedParserId,
      }),
    }
  )
);

export interface ArraySubField {
  name: string;
  type: "string" | "number" | "boolean";
  description: string;
}

export interface SchemaField {
  id: string;
  name: string;
  type: "string" | "number" | "boolean" | "enum" | "date" | "array";
  description: string;
  enumValues?: string[];
  arrayFields?: ArraySubField[];
}

export const FIELD_TYPE_OPTIONS = [
  { value: "string" as const, label: "Texto" },
  { value: "number" as const, label: "Número" },
  { value: "boolean" as const, label: "Sí/No" },
  { value: "enum" as const, label: "Opciones" },
  { value: "date" as const, label: "Fecha" },
  { value: "array" as const, label: "Lista" },
];

export const VALIDATION_FIELD: SchemaField = {
  id: "is_valid_document",
  name: "is_valid_document",
  type: "boolean",
  description:
    "True si el documento corresponde al tipo esperado, False si no lo es",
};

export interface SchemaTemplate {
  label: string;
  description: string;
  fields: Omit<SchemaField, "id">[];
}

export const TEMPLATES: SchemaTemplate[] = [
  {
    label: "Estado de cuenta bancaria",
    description: "Campos típicos de un estado de cuenta",
    fields: [
      {
        name: "owner",
        type: "string",
        description: "Nombre completo del titular de la cuenta",
      },
      {
        name: "account_number",
        type: "string",
        description: "Número CLABE de 18 dígitos",
      },
      {
        name: "bank_name",
        type: "enum",
        description: "Nombre del banco emisor",
        enumValues: [
          "ABC CAPITAL", "ACTINVER", "AFIRME", "AKALA", "ALTERNATIVOS",
          "ARCUS", "ASP INTEGRA OPC", "AUTOFIN", "AZTECA", "BAJIO",
          "BANAMEX", "BANCO FINTERRA", "BANCO S3", "BANCOMEXT", "BANCOPPEL",
          "BANCREA", "BANJERCITO", "BANK OF AMERICA", "BANKAOOL", "BANOBRAS",
          "BANORTE", "BANREGIO", "BANSEFI", "BANSI", "BANXICO", "BARCLAYS",
          "BBASE", "BBVA MEXICO", "BMONEX", "CAJA POP MEXICA",
          "CAJA TELEFONIST", "CB INTERCAM", "CI BOLSA", "CIBANCO",
          "COMPARTAMOS", "CONSUBANCO", "CREDICAPITAL", "CREDIT SUISSE",
          "CRISTOBAL COLON", "CoDi Valida", "DONDE", "EVERCORE", "FINAMEX",
          "FINCOMUN", "FOMPED", "FONDO (FIRA)", "GBM", "GEM - STP",
          "HIPOTECARIA FED", "HSBC", "ICBC", "INBURSA", "INDEVAL",
          "INMOBILIARIO", "INTERCAM BANCO", "INVERCAP", "INVEX", "JP MORGAN",
          "KUSPIT", "LIBERTAD", "MASARI", "MIFEL", "MIZUHO BANK", "MONEXCB",
          "MUFG", "MULTIVA BANCO", "MULTIVA CBOLSA", "NAFIN", "PAGATODO",
          "PROFUTURO", "REFORMA", "SABADELL", "SANTANDER", "SCOTIABANK",
          "SHINHAN", "STP", "TRANSFER", "UNAGRA", "VALMEX", "VALUE",
          "VE POR MAS", "VECTOR", "VOLKSWAGEN",
        ],
      },
    ],
  },
  {
    label: "Factura",
    description: "Campos típicos de una factura",
    fields: [
      {
        name: "emisor",
        type: "string",
        description: "Nombre o razón social del emisor",
      },
      {
        name: "receptor",
        type: "string",
        description: "Nombre o razón social del receptor",
      },
      {
        name: "total",
        type: "number",
        description: "Monto total de la factura",
      },
      {
        name: "fecha",
        type: "date",
        description: "Fecha de emisión de la factura",
      },
    ],
  },
  {
    label: "En blanco",
    description: "Empezar sin campos predefinidos",
    fields: [],
  },
];

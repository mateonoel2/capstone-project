# *Frontend* de Extracción de Estados de Cuenta Bancarios

Una aplicación de *frontend* en *Next.js* para extraer y verificar información de cuentas bancarias desde estados de cuenta en PDF. Esta aplicación proporciona una interfaz moderna y amigable para subir estados de cuenta bancarios en PDF, verlos lado a lado con los datos extraídos, hacer correcciones y enviar resultados verificados.

## Características

- **Carga de PDF**: Arrastra y suelta o haz clic para subir estados de cuenta bancarios en PDF
- **Vista Lado a Lado**: Ver el documento PDF junto al formulario de extracción
- **Extracción en Tiempo Real**: Extracción automática usando *Claude AI* cuando se sube un PDF
- **Verificación de Datos**: Editar y corregir información extraída antes de enviar
- **Seguimiento de Cambios**: Indicadores visuales muestran qué campos han sido modificados de la extracción original
- ***Logging* de Datos**: Todas las extracciones y correcciones se registran en la base de datos del *backend* para seguimiento de precisión

## *Stack* Tecnológico

- ***Framework***: *Next.js* 15 con *App Router*
- **Lenguaje**: *TypeScript*
- **Estilos**: *Tailwind CSS*
- **Componentes de Interfaz**: *shadcn/ui* (primitivos de *Radix UI*)
- **Visor de PDF**: *react-pdf*
- **Iconos**: *Lucide React*

## Prerequisitos

- Node.js 18+
- npm, yarn, o pnpm
- API del *backend* ejecutándose en http://localhost:8000

## Instalación

1. Navegar al directorio del *frontend*:

```bash
cd frontend
```

2. Instalar dependencias:

```bash
npm install
# o
yarn install
# o
pnpm install
```

## Desarrollo

Ejecutar el servidor de desarrollo:

```bash
npm run dev
# o
yarn dev
# o
pnpm dev
```

Abrir [http://localhost:3000](http://localhost:3000) en tu navegador.

## Construcción para Producción

```bash
npm run build
npm run start
```

## Estructura del Proyecto

```
frontend/
├── app/
│   ├── layout.tsx          # Layout raíz con metadata
│   ├── page.tsx             # Página principal de extracción
│   └── globals.css          # Estilos globales y variables CSS
├── components/
│   ├── ui/                  # Componentes shadcn/ui
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── label.tsx
│   ├── file-upload.tsx      # Componente de carga con arrastrar y soltar
│   └── pdf-viewer.tsx       # Visor de documentos PDF
├── lib/
│   ├── api.ts               # Cliente de API para comunicación con backend
│   ├── utils.ts             # Funciones de utilidad (helper cn)
│   └── pdf-worker.ts        # Configuración del worker de PDF.js
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.mjs
```

## Integración con la API

El *frontend* se comunica con la API del *backend* usando dos *endpoints* principales:

### 1. Extraer desde PDF
- ***Endpoint***: `POST /extraction/pdf`
- **Propósito**: Subir un PDF y recibir datos extraídos
- **Respuesta**: `{ owner, bank_name, account_number }`

### 2. Enviar Extracción
- ***Endpoint***: `POST /extraction/submit`
- **Propósito**: Enviar datos verificados con seguimiento de correcciones
- ***Payload***:

```json
{
  "filename": "statement.pdf",
  "extracted_owner": "Original Name",
  "extracted_bank_name": "Original Bank",
  "extracted_account_number": "123456",
  "final_owner": "Corrected Name",
  "final_bank_name": "Corrected Bank",
  "final_account_number": "123456"
}
```

## Variables de Entorno

Crear un archivo `.env.local` para personalizar la URL de la API:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Flujo de Uso

1. **Subir**: Usuario sube un estado de cuenta bancario en PDF
2. **Extraer**: El *backend* automáticamente extrae titular, nombre del banco y número de cuenta
3. **Revisar**: Usuario revisa los datos extraídos mientras ve el PDF
4. **Corregir**: Usuario edita cualquier campo incorrecto (resaltado en amarillo)
5. **Enviar**: Usuario envía los datos verificados
6. **Registrar**: El *backend* registra tanto los datos originales como los corregidos para seguimiento de precisión

## Indicadores Visuales

- **Borde Amarillo**: El campo ha sido modificado de la extracción original
- **Texto Amarillo**: Muestra el valor extraído original para comparación
- **Banner Amarillo**: Indica que se han hecho cambios a los datos
- **Estados de Carga**: *Spinners* durante extracción y envío
- **Mensajes de Éxito/Error**: Retroalimentación clara para todas las operaciones

## Teclado y Accesibilidad

- Los *inputs* del formulario son completamente accesibles por teclado
- Etiquetas ARIA adecuadas para lectores de pantalla
- Estados de *focus* para todos los elementos interactivos
- Estructura HTML semántica

## Mejoras Futuras (Fase 2)

- Página de *dashboard* con métricas de extracción
- Estadísticas de precisión y gráficos
- Historial de extracción filtrable
- Funcionalidad de exportación para datos registrados
- Autenticación de usuarios

## Solución de Problemas

### PDF No Carga

- Asegúrate de que *react-pdf* esté instalado correctamente
- Verifica la consola del navegador para errores del *worker* de *PDF.js*
- Verifica que el archivo PDF no esté corrupto

### Errores de Conexión con la API

- Confirma que el *backend* esté ejecutándose en http://localhost:8000
- Verifica la configuración de CORS en el *backend*
- Verifica las solicitudes de red en *DevTools* del navegador

### Errores de Construcción

- Limpia el directorio `.next`: `rm -rf .next`
- Elimina `node_modules` y reinstala: `rm -rf node_modules && npm install`
- Verifica errores de *TypeScript*: `npm run lint`

## Licencia

Parte del proyecto *capstone* de Extracción de Estados de Cuenta Bancarios.

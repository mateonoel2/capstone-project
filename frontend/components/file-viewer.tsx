"use client";

import { useState } from "react";
import { PDFViewer } from "./pdf-viewer";
import { ZoomIn, ZoomOut, RotateCw } from "lucide-react";

interface FileViewerProps {
  file: File;
}

function ImageViewer({ file }: FileViewerProps) {
  const [scale, setScale] = useState(1.0);
  const [rotation, setRotation] = useState(0);
  const [url] = useState(() => URL.createObjectURL(file));

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto border rounded-lg bg-gray-50">
        <div className="p-4 flex justify-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={url}
            alt={file.name}
            style={{
              transform: `scale(${scale}) rotate(${rotation}deg)`,
              transformOrigin: "center center",
              maxWidth: "100%",
            }}
            className="shadow-lg transition-transform"
          />
        </div>
      </div>
      <div className="flex items-center justify-center gap-2 p-2 bg-gray-100 rounded mt-4">
        <button
          onClick={() => setScale((s) => Math.max(s - 0.1, 0.1))}
          disabled={scale <= 0.1}
          className="px-3 py-2 bg-white border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          title="Zoom Out"
        >
          <ZoomOut className="h-4 w-4" />
        </button>
        <span className="text-sm font-medium min-w-[80px] text-center">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={() => setScale((s) => Math.min(s + 0.1, 3.0))}
          disabled={scale >= 3.0}
          className="px-3 py-2 bg-white border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          title="Zoom In"
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        <button
          onClick={() => setRotation((r) => (r + 90) % 360)}
          className="px-3 py-2 bg-white border rounded hover:bg-gray-50 flex items-center gap-1 ml-2"
          title="Rotate"
        >
          <RotateCw className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

export function FileViewer({ file }: FileViewerProps) {
  const isPDF = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");

  if (isPDF) {
    return <PDFViewer file={file} />;
  }

  return <ImageViewer file={file} />;
}

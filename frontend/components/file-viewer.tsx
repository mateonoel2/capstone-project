"use client";

import { useState, useRef, useCallback } from "react";
import {
  TransformWrapper,
  TransformComponent,
  useControls,
  type ReactZoomPanPinchRef,
} from "react-zoom-pan-pinch";
import { ZoomIn, ZoomOut, Minimize2, RotateCw } from "lucide-react";

interface FileViewerProps {
  file: File;
}

export function FileViewer({ file }: FileViewerProps) {
  const [url] = useState(() => URL.createObjectURL(file));
  const [rotation, setRotation] = useState(0);
  const isPDF =
    file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  const transformRef = useRef<ReactZoomPanPinchRef>(null);

  const onWheel = useCallback((e: React.WheelEvent) => {
    // ctrlKey is set for trackpad pinch gestures
    if (e.ctrlKey) {
      e.preventDefault();
      const ref = transformRef.current;
      if (!ref) return;
      if (e.deltaY < 0) {
        ref.zoomIn(0.1, 0);
      } else {
        ref.zoomOut(0.1, 0);
      }
    }
  }, []);

  const handleRotate = useCallback(() => {
    setRotation((r) => (r + 90) % 360);
  }, []);

  if (isPDF) {
    return (
      <iframe
        src={url}
        title={file.name}
        className="w-full h-full border rounded-lg"
      />
    );
  }

  return (
    <div className="w-full h-full border rounded-lg bg-gray-50 flex flex-col">
      <TransformWrapper
        initialScale={1}
        minScale={0.1}
        maxScale={10}
        centerOnInit
        pinch={{ step: 5 }}
        wheel={{ disabled: true }}
        ref={transformRef}
      >
        <ImageControls onRotate={handleRotate} />
        <TransformComponent
          wrapperStyle={{ width: "100%", flex: 1 }}
          wrapperProps={{ onWheel: onWheel }}
          contentStyle={{
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={url}
            alt={file.name}
            className="max-w-full max-h-full object-contain transition-transform duration-200"
            style={{ transform: `rotate(${rotation}deg)` }}
          />
        </TransformComponent>
      </TransformWrapper>
    </div>
  );
}

function ImageControls({ onRotate }: { onRotate: () => void }) {
  const { zoomIn, zoomOut, resetTransform } = useControls();
  return (
    <div className="flex items-center justify-center gap-1 p-2 border-b bg-gray-100">
      <button
        onClick={() => zoomOut()}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
      >
        <ZoomOut className="h-3.5 w-3.5" />
        <span>Alejar</span>
      </button>
      <button
        onClick={() => zoomIn()}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
      >
        <ZoomIn className="h-3.5 w-3.5" />
        <span>Acercar</span>
      </button>
      <button
        onClick={() => resetTransform()}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
      >
        <Minimize2 className="h-3.5 w-3.5" />
        <span>Restablecer</span>
      </button>
      <button
        onClick={onRotate}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
      >
        <RotateCw className="h-3.5 w-3.5" />
        <span>Rotar</span>
      </button>
    </div>
  );
}

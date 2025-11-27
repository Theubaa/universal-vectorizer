import { useCallback, useState } from "react";

const Dropzone = ({ onFilesSelected, disabled = false }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      if (disabled) return;
      setIsDragging(false);
      const files = event.dataTransfer.files;
      onFilesSelected(files);
    },
    [disabled, onFilesSelected],
  );

  const handleDragOver = (event) => {
    event.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleFileChange = (event) => {
    if (!disabled) {
      onFilesSelected(event.target.files);
    }
  };

  return (
    <div
      className={`dropzone ${isDragging ? "dragging" : ""} ${disabled ? "disabled" : ""}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <p>Drag and drop files here or click to browse</p>
      <input type="file" multiple disabled={disabled} onChange={handleFileChange} />
      <small>PDF, text, images, audio, CSV/Excel, JSON, and URLs</small>
    </div>
  );
};

export default Dropzone;



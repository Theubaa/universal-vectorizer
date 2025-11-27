const MetadataModal = ({ metadata, onClose }) => {
  if (!metadata) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <header>
          <h3>Metadata</h3>
          <button type="button" onClick={onClose}>
            Close
          </button>
        </header>
        <div className="modal-content">
          {Object.entries(metadata).map(([key, value]) => (
            <div key={key} className="metadata-row">
              <span>{key}</span>
              <strong>{String(value)}</strong>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MetadataModal;


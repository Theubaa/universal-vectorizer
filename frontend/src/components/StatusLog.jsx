const StatusLog = ({ entries }) => {
  return (
    <div className="status-log">
      <h3>Ingestion Status</h3>
      <div className="log-entries">
        {entries.length === 0 && <p>No ingestions so far.</p>}
        {entries.map((entry) => (
          <div key={entry.id} className={`log-entry ${entry.state}`}>
            <div>
              <strong>{entry.filename}</strong>
              <span>{entry.timestamp}</span>
            </div>
            <p>{entry.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatusLog;



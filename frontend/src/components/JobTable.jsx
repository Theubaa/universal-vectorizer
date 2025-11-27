import ProgressBar from "./ProgressBar";

const JobTable = ({ jobs }) => {
  if (!jobs.length) {
    return <p className="muted">No ingestion jobs yet.</p>;
  }

  return (
    <div className="job-table">
      <div className="job-table__header">
        <span>Job</span>
        <span>Status</span>
        <span>Chunks</span>
        <span>Progress</span>
        <span>Last message</span>
      </div>
      {jobs.map((job) => {
        const progress =
          job.total_chunks && job.total_chunks > 0 ? job.processed_chunks / job.total_chunks : null;
        return (
          <div key={job.job_id} className="job-table__row">
            <div>
              <strong>{job.displayName ?? job.source}</strong>
              <small>{job.job_id}</small>
            </div>
            <span className={`badge ${job.state}`}>{job.state}</span>
            <span>{job.processed_chunks}</span>
            <div>{progress !== null ? <ProgressBar value={progress} /> : <span className="muted">Streaming</span>}</div>
            <span>{job.last_message ?? "—"}</span>
          </div>
        );
      })}
    </div>
  );
};

export default JobTable;


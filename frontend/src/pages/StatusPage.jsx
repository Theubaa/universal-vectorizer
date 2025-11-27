import { useEffect, useState } from "react";
import JobTable from "../components/JobTable";
import { health, listJobs } from "../services/api";

const StatusPage = () => {
  const [backendStatus, setBackendStatus] = useState("unknown");
  const [jobs, setJobs] = useState([]);

  const refresh = async () => {
    try {
      await health();
      setBackendStatus("online");
    } catch {
      setBackendStatus("offline");
    }
    const jobData = await listJobs();
    setJobs(jobData);
  };

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <section className="panel">
      <div className="status-header">
        <h2>Ingestion Operations</h2>
        <div className={`badge ${backendStatus}`}>API {backendStatus}</div>
        <button type="button" onClick={refresh}>
          Refresh
        </button>
      </div>
      <JobTable jobs={jobs} />
    </section>
  );
};

export default StatusPage;



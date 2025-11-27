import { useEffect, useRef, useState } from "react";
import Dropzone from "../components/Dropzone";
import JobTable from "../components/JobTable";
import { ingestFile, ingestUrl, listJobs, uploadFile, watchJob } from "../services/api";

const UploadPage = () => {
  const [jobs, setJobs] = useState({});
  const [url, setUrl] = useState("");
  const [tag, setTag] = useState("");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const subscriptions = useRef({});

  useEffect(() => {
    const bootstrap = async () => {
      const existing = await listJobs();
      setJobs((prev) => {
        const next = { ...prev };
        existing.forEach((job) => {
          next[job.job_id] = job;
        });
        return next;
      });
    };
    bootstrap();
    return () => {
      Object.values(subscriptions.current).forEach((cleanup) => cleanup?.());
    };
  }, []);

  const trackJob = (jobId, label) => {
    setJobs((prev) => ({
      ...prev,
      [jobId]: {
        job_id: jobId,
        kind: "file",
        source: label,
        state: "pending",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        processed_chunks: 0,
        total_chunks: null,
        errors: [],
      },
    }));

    const cleanup = watchJob(jobId, (payload) =>
      setJobs((prev) => ({
        ...prev,
        [jobId]: { ...payload, displayName: label ?? payload.source },
      })),
    );
    subscriptions.current[jobId] = cleanup;
  };

  const handleFilesSelected = async (fileList) => {
    setBusy(true);
    for (const file of Array.from(fileList)) {
      try {
        const { file_path: filePath } = await uploadFile(file);
        const metadata = {};
        if (tag) metadata.tag = tag;
        if (notes) metadata.notes = notes;
        const { job_id: jobId } = await ingestFile(filePath, metadata);
        trackJob(jobId, file.name);
      } catch (error) {
        console.error(error);
      }
    }
    setBusy(false);
  };

  const handleUrlIngest = async (event) => {
    event.preventDefault();
    if (!url) return;
    setBusy(true);
    try {
      const metadata = {};
      if (tag) metadata.tag = tag;
      const { job_id: jobId } = await ingestUrl(url, metadata);
      trackJob(jobId, url);
      setUrl("");
    } catch (error) {
      console.error(error);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="panel">
      <h2>Upload & Ingest</h2>
      <div className="form-row">
        <input placeholder="Tag (e.g. contract, ticket, dataset)" value={tag} onChange={(e) => setTag(e.target.value)} />
        <input placeholder="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
      </div>
      <Dropzone onFilesSelected={handleFilesSelected} disabled={busy} />
      <form className="url-form" onSubmit={handleUrlIngest}>
        <input
          type="url"
          placeholder="https://example.com/article"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit" disabled={busy}>
          Ingest URL
        </button>
      </form>
      <JobTable jobs={Object.values(jobs)} />
    </section>
  );
};

export default UploadPage;



import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_BASE =
  import.meta.env.VITE_WS_URL ||
  API_BASE.replace("https://", "wss://").replace("http://", "ws://");

const client = axios.create({
  baseURL: API_BASE,
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const ingestFile = async (filePath, metadata = {}) => {
  const { data } = await client.post("/ingest", { file_path: filePath, metadata });
  return data;
};

export const ingestUrl = async (url, metadata = {}) => {
  const { data } = await client.post("/ingest", { url, metadata });
  return data;
};

export const listJobs = async () => {
  const { data } = await client.get("/ingest/jobs");
  return data.jobs;
};

export const getJobStatus = async (jobId) => {
  const { data } = await client.get(`/ingest/${jobId}/status`);
  return data;
};

export const subscribeToJob = (jobId, onUpdate) => {
  try {
    const socket = new WebSocket(`${WS_BASE}/ws/ingest/${jobId}`);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      onUpdate(payload);
    };
    socket.onerror = () => socket.close();
    return () => socket.close();
  } catch (error) {
    console.warn("WebSocket subscription failed", error);
    return null;
  }
};

export const watchJob = (jobId, onUpdate) => {
  const wsCleanup = subscribeToJob(jobId, onUpdate);
  const interval = setInterval(async () => {
    try {
      const status = await getJobStatus(jobId);
      onUpdate(status);
    } catch (error) {
      console.error("Job poll failed", error);
    }
  }, 4000);

  return () => {
    if (wsCleanup) wsCleanup();
    clearInterval(interval);
  };
};

export const search = async ({ query, topK = 5, offset = 0, filters = null }) => {
  const payload = { query, top_k: topK, offset, filters };
  const { data } = await client.post("/search", payload);
  return data;
};

export const health = async () => {
  const { data } = await client.get("/health");
  return data;
};



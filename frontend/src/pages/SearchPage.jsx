import { useState } from "react";
import MetadataModal from "../components/MetadataModal";
import SearchResultCard from "../components/SearchResultCard";
import { search } from "../services/api";

const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(6);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState({ type: "", source: "" });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [modalMetadata, setModalMetadata] = useState(null);

  const executeSearch = async (pageOverride) => {
    if (!query) return;
    setLoading(true);
    setError("");
    try {
      const payloadFilters = {};
      if (filters.type) payloadFilters.type = filters.type;
      if (filters.source) payloadFilters.source = filters.source;
      const data = await search({
        query,
        topK,
        offset: pageOverride * topK,
        filters: Object.keys(payloadFilters).length ? payloadFilters : null,
      });
      setResults(data.matches);
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (event) => {
    event?.preventDefault();
    setPage(0);
    await executeSearch(0);
  };

  const handlePageChange = async (direction) => {
    const nextPage = Math.max(0, page + direction);
    setPage(nextPage);
    await executeSearch(nextPage);
  };

  return (
    <section className="panel">
      <h2>Semantic Search</h2>
      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about your ingested data..."
        />
        <input
          type="number"
          value={topK}
          min={1}
          max={50}
          onChange={(e) => setTopK(Number(e.target.value))}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      <div className="filter-row">
        <input
          placeholder="Filter by type (pdf, text, json...)"
          value={filters.type}
          onChange={(e) => setFilters((prev) => ({ ...prev, type: e.target.value }))}
        />
        <input
          placeholder="Filter by source"
          value={filters.source}
          onChange={(e) => setFilters((prev) => ({ ...prev, source: e.target.value }))}
        />
        <button type="button" onClick={() => handlePageChange(-1)} disabled={page === 0 || loading}>
          Prev
        </button>
        <button type="button" onClick={() => handlePageChange(1)} disabled={loading}>
          Next
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      <div className="results-grid">
        {results.map((result) => (
          <SearchResultCard key={result.id} result={result} onInspect={(metadata) => setModalMetadata(metadata)} />
        ))}
      </div>
      <MetadataModal metadata={modalMetadata} onClose={() => setModalMetadata(null)} />
    </section>
  );
};

export default SearchPage;



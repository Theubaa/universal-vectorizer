const SearchResultCard = ({ result, onInspect }) => {
  return (
    <article className="search-card">
      <header>
        <span>{result.metadata?.type ?? "unknown"}</span>
        <strong title={result.metadata?.source}>{result.metadata?.source ?? "N/A"}</strong>
      </header>
      <p>{result.text}</p>
      <footer>
        <span>Score: {result.score.toFixed(4)}</span>
        <span>Chunk: {result.metadata?.chunk_index ?? "-"}</span>
        <button type="button" onClick={() => onInspect(result.metadata)}>
          Metadata
        </button>
      </footer>
    </article>
  );
};

export default SearchResultCard;



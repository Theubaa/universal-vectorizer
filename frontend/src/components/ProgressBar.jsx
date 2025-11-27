const ProgressBar = ({ value }) => {
  const percentage = Math.min(Math.max(value ?? 0, 0), 1) * 100;
  return (
    <div className="progress-outer">
      <div className="progress-inner" style={{ width: `${percentage}%` }} />
    </div>
  );
};

export default ProgressBar;


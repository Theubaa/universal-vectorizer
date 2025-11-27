import { NavLink, Route, Routes } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import StatusPage from "./pages/StatusPage";
import SearchPage from "./pages/SearchPage";

const App = () => {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Universal Vectorizer</h1>
        <nav>
          <NavLink to="/" end>
            Upload
          </NavLink>
          <NavLink to="/status">Status</NavLink>
          <NavLink to="/search">Search</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/status" element={<StatusPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;



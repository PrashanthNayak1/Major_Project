import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Encode from "./pages/Encode";
import Decode from "./pages/Decode";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <div className="page-container">
          <Routes>
            <Route path="/" element={<Encode />} />
            <Route path="/encode" element={<Encode />} />
            <Route path="/decode" element={<Decode />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;

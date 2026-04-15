import React from "react";
import { Link } from "react-router-dom";
import "./Sidebar.css";

export default function Sidebar() {
  return (
    <div className="sidebar">
      <h2 className="logo">V-Stego</h2>

      <Link to="/encode" className="nav-btn">Encode</Link>
      <Link to="/decode" className="nav-btn">Decode</Link>
    </div>
  );
}

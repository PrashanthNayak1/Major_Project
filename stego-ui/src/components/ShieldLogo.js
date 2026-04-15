// src/components/ShieldLogo.js
import React from "react";
import "./shield.css";

function ShieldLogo({ active, label }) {
  return (
    <div className={`shield-wrapper ${active ? "shield-active" : ""}`}>
      <div className="shield-ring"></div>
      <svg
        className="shield-icon"
        viewBox="0 0 64 64"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00ff99" />
            <stop offset="100%" stopColor="#00d47a" />
          </linearGradient>
        </defs>
        <path
          d="M32 4 L14 10 V28 C14 40 21 50 32 56 C43 50 50 40 50 28 V10 Z"
          fill="url(#shieldGradient)"
          stroke="#00ffcc"
          strokeWidth="1.5"
        />
        <path
          d="M24 32 L30 38 L42 24"
          fill="none"
          stroke="#021b16"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {label && <div className="shield-label">{label}</div>}
    </div>
  );
}

export default ShieldLogo;

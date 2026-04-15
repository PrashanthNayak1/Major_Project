// src/components/CircleProgress.js
import React from "react";
import "./circle.css";

function CircleProgress({ value = 0 }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="progress-shell">
      <svg className="progress-ring" viewBox="0 0 120 120">
        <circle
          className="ring-bg"
          cx="60"
          cy="60"
          r={radius}
        />
        <circle
          className="ring-fg"
          cx="60"
          cy="60"
          r={radius}
          style={{
            strokeDasharray: circumference,
            strokeDashoffset: offset,
          }}
        />
      </svg>
      <div className="progress-center-text">
        <span>{Math.round(value)}%</span>
      </div>
    </div>
  );
}

export default CircleProgress;

import React, { useState } from "react";
import axios from "axios";
import CircleProgress from "../components/CircleProgress";
import ShieldLogo from "../components/ShieldLogo";
import toast from "react-hot-toast";
import "./Encode.css";

const API = "http://127.0.0.1:8000/encode";

function Encode() {
  const [video, setVideo] = useState(null);
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  // Smooth UI-based progress animation
  const startSmoothProgress = () => {
    let p = 0;
    const interval = setInterval(() => {
      p += Math.floor(Math.random() * 7) + 3; // 3–9% increments
      if (p >= 95) p = 95;
      setProgress(p);
    }, 600);
    return interval;
  };

  const handleEncode = async () => {
    if (!video || !file || !password) {
      toast.error("Please select a video, a file, and enter a password!");
      return;
    }

    setProgress(1);
    setLoading(true);
    const fakeLoop = startSmoothProgress();

    const formData = new FormData();
    formData.append("video", video);
    formData.append("file", file);
    formData.append("password", password);

    try {
      const res = await axios.post(API, formData, { responseType: "blob" });

      clearInterval(fakeLoop);
      setProgress(100);

      const disp = res.headers["content-disposition"];
      let filename = "stego_video.mkv";
      if (disp && disp.includes("filename="))
        filename = disp.split("filename=")[1].replace(/"/g, "");

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();

      toast.success("Video successfully encoded & saved! 🔐");
    } catch (err) {
      clearInterval(fakeLoop);
      setProgress(0);
      toast.error("Encoding failed. Please try again!");
    }

    setLoading(false);
  };

  return (
    <div className="page-root">
      <div className="encode-container glass-panel">
        <div className="encode-header">
          <ShieldLogo active={loading} label={loading ? "Encoding" : "V-Stego"} />
          <div className="encode-title-block">
            <h2>🔐 Video Steganography</h2>
            <p>Hide any file securely inside a lossless video stream.</p>
          </div>
        </div>

        {!loading && (
          <div className="encode-form">
            <label className="field-label">Cover Video (.mkv recommended)</label>
            <input
              type="file"
              accept=".mkv,video/*"
              onChange={(e) => setVideo(e.target.files[0])}
            />

            <label className="field-label">Secret File</label>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />

            <label className="field-label">Password</label>
            <input
              type="password"
              placeholder="Enter encryption password"
              onChange={(e) => setPassword(e.target.value)}
            />

            <button className="primary-btn" onClick={handleEncode}>
              Start Encoding
            </button>
          </div>
        )}

        {loading && (
          <div className="encode-progress-block">
            <CircleProgress value={progress} />
            <p className="status-text">Encoding {Math.round(progress)}%</p>
            <p className="hint-text">
              Encrypting payload, embedding stream and reconstructing video…
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Encode;

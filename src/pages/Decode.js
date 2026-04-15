import React, { useState } from "react";
import axios from "axios";
import CircleProgress from "../components/CircleProgress";
import ShieldLogo from "../components/ShieldLogo";
import toast from "react-hot-toast";
import "./Decode.css";

const API = "http://127.0.0.1:8000/decode";

function Decode() {
  const [video, setVideo] = useState(null);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const startSmoothProgress = () => {
    let p = 0;
    const interval = setInterval(() => {
      p += Math.floor(Math.random() * 8) + 2; // 2–10%
      if (p >= 95) p = 95;
      setProgress(p);
    }, 600);
    return interval;
  };

  const handleDecode = async () => {
    if (!video || !password) {
      toast.error("Select a stego video and enter password!");
      return;
    }

    setProgress(1);
    setLoading(true);
    const fakeLoop = startSmoothProgress();

    const formData = new FormData();
    formData.append("stego_video", video);
    formData.append("password", password);

    try {
      const res = await axios.post(API, formData, { responseType: "blob" });

      clearInterval(fakeLoop);
      setProgress(100);

      const disp = res.headers["content-disposition"];
      let filename = "recovered_file";
      if (disp && disp.includes("filename="))
        filename = disp.split("filename=")[1].replace(/"/g, "");

      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();

      toast.success("Hidden file successfully recovered! 🔓");
    } catch (err) {
      clearInterval(fakeLoop);
      setProgress(0);
      toast.error("Decoding failed — wrong password or corrupted video!");
    }

    setLoading(false);
  };

  return (
    <div className="page-root">
      <div className="decode-container glass-panel">
        <div className="decode-header">
          <ShieldLogo active={loading} label={loading ? "Decoding" : "V-Stego"} />
          <div className="decode-title-block">
            <h2>🔍 Extract Hidden Payload</h2>
            <p>Recover the encrypted file hidden inside a stego video.</p>
          </div>
        </div>

        {!loading && (
          <div className="decode-form">
            <label className="field-label">Stego Video (.mkv from encoder)</label>
            <input
              type="file"
              accept=".mkv,video/*"
              onChange={(e) => setVideo(e.target.files[0])}
            />

            <label className="field-label">Password</label>
            <input
              type="password"
              placeholder="Enter encoding password"
              onChange={(e) => setPassword(e.target.value)}
            />

            <button className="primary-btn" onClick={handleDecode}>
              Start Decoding
            </button>
          </div>
        )}

        {loading && (
          <div className="decode-progress-block">
            <CircleProgress value={progress} />
            <p className="status-text">Decoding {Math.round(progress)}%</p>
            <p className="hint-text">
              Reading frames, verifying cryptographic tag, restoring original file…
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Decode;

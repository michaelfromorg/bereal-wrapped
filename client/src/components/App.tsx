import axios from "axios";
import React, { useState } from "react";
import "../styles/App.css";

type Stage = "phoneInput" | "otpInput" | "settings" | "videoDisplay";

const IS_PRODUCTION = process.env.NODE_ENV === "production";
const BASE_URL = IS_PRODUCTION
  ? "https://bereal-api.michaeldemar.co"
  : "http://localhost:5000";

const App: React.FC = () => {
  const [stage, setStage] = useState<Stage>("phoneInput");
  const [phoneNumber, setPhoneNumber] = useState<string>("");
  const [countryCode, setCountryCode] = useState<string>("");
  const [otp, setOtp] = useState<string>("");
  const [year, setYear] = useState<string>("2022");
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<string>("classic");
  const [videoUrl, setVideoUrl] = useState<string>("");

  const handlePhoneSubmit = async () => {
    try {
      const response = await axios.post(`${BASE_URL}/request-otp`, {
        phone: `${countryCode}${phoneNumber}`,
      });

      // Handle response, e.g., display a message or store the session info
      console.log(response.data);
      setStage("otpInput");
    } catch (error) {
      console.error("Error sending OTP:", error);
      // Handle error, e.g., display an error message to the user
    }
  };

  const handleOtpSubmit = async () => {
    try {
      const response = await axios.post(`${BASE_URL}/validate-otp`, {
        phone: `${countryCode}${phoneNumber}`,
        otp,
      });
      // Handle response, e.g., move to the next stage
      console.log(response.data);
      setStage("settings");
    } catch (error) {
      console.error("Error validating OTP:", error);
      // Handle error
    }
  };

  const handleSettingsSubmit = async () => {
    // FormData to handle file upload
    const formData = new FormData();
    formData.append("phone", `${countryCode}${phoneNumber}`);
    formData.append("year", year);
    formData.append("mode", mode);
    if (file) {
      formData.append("file", file);
    }

    try {
      const response = await axios.post(`${BASE_URL}/video`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      // Assume response contains the video URL
      setVideoUrl(response.data.videoUrl);
      setStage("videoDisplay");
    } catch (error) {
      console.error("Error submitting settings:", error);
      // Handle error
    }
  };

  return (
    <div className="App">
      <h1 className="text-4xl font-bold text-center mb-6">BeReal. Recap.</h1>
      <div>
        {stage === "phoneInput" && (
          <>
            <label
              htmlFor="countryCode"
              className="block text-sm font-medium text-gray-700"
            >
              Country Code
            </label>
            <input
              type="text"
              id="countryCode"
              placeholder="Country Code"
              value={countryCode}
              onChange={(e) => setCountryCode(e.target.value)}
            />
            <label
              htmlFor="phoneNumber"
              className="block text-sm font-medium text-gray-700"
            >
              Phone Number
            </label>
            <input
              type="text"
              id="phoneNumber"
              placeholder="Phone Number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
            />
            <button onClick={handlePhoneSubmit}>Send OTP</button>
          </>
        )}
        {stage === "otpInput" && (
          <>
            <label
              htmlFor="otp"
              className="block text-sm font-medium text-gray-700"
            >
              One-Time Password
            </label>
            <input
              type="text"
              id="otp"
              placeholder="OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <button onClick={handleOtpSubmit}>Validate OTP</button>
          </>
        )}
        {stage === "settings" && (
          <>
            <label
              htmlFor="year"
              className="block text-sm font-medium text-gray-700"
            >
              Year
            </label>
            <select
              id="year"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            >
              <option value="2022">2022</option>
              <option value="2023">2023</option>
            </select>
            <label
              htmlFor="song"
              className="block text-sm font-medium text-gray-700"
            >
              Song
            </label>
            <input
              type="file"
              id="song"
              accept=".wav"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            <label
              htmlFor="mode"
              className="block text-sm font-medium text-gray-700"
            >
              Mode
            </label>
            <select
              id="mode"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              <option value="classic">Classic (30 seconds)</option>
              <option value="full">Full</option>
            </select>
            <button onClick={handleSettingsSubmit}>Submit Settings</button>
          </>
        )}
        {stage === "videoDisplay" && (
          <>
            <video src={videoUrl} controls />
            <button onClick={() => (window.location.href = videoUrl)}>
              Download Video
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default App;

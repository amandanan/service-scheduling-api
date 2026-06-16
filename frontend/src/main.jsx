import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ToastContainer } from "react-toastify";

import "react-toastify/dist/ReactToastify.css";

import "./styles/global.css";
import "./styles/variables.css";

import App from "./App.jsx";

// Apply the persisted theme before first paint so there's no flash.
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
  document.documentElement.setAttribute("data-theme", savedTheme);
}

createRoot(document.getElementById("root")).render(
  <StrictMode>

    <App />

    <ToastContainer
      position="top-right"
      autoClose={3000}
      theme="dark"
    />

  </StrictMode>
);

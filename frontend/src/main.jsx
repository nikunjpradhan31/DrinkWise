// src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";
import { AuthContextProvider } from "./context/AuthContext";

// const enableMocking = async () => {
//   if (!import.meta.env.DEV) {
//     return;
//   }

//   const { worker } = await import("./mocks/browser");
//   await worker.start({
//     onUnhandledRequest: "bypass",
//   });
// };

  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <BrowserRouter>
        <AuthContextProvider>
          <App />
        </AuthContextProvider>
      </BrowserRouter>
    </React.StrictMode>
  );


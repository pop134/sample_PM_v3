import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { AuthProvider } from "./features/auth/AuthContext";
import { LocationProvider } from "./features/locations/LocationContext";
import { ThemeProvider } from "./theme/ThemeContext";
import "./styles/index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <LocationProvider>
          <App />
        </LocationProvider>
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>,
);

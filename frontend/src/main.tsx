import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import { LanguageProvider } from "./lib/i18n";
import "./index.css";

const container = document.getElementById("root");

if (!container) {
  throw new Error("Root element #root was not found.");
}

createRoot(container).render(
  <StrictMode>
    <LanguageProvider>
      <App />
    </LanguageProvider>
  </StrictMode>,
);

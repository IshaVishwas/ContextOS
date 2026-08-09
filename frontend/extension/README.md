# ContextOS Browser Extension v1.0

The ContextOS Browser Extension seamlessly integrates your chat activities (ChatGPT, Gemini, Claude) with the Context Virtualization Engine backend.

## Architecture

This extension is built with **Manifest V3** and follows **SOLID** principles:
- **`background.js`**: Service worker acting as the central communications hub.
- **`content.js`**: Bootstraps observers into active tabs.
- **`observer.js`**: Core event listener intercepting Enter keys and submit clicks.
- **`providers/`**: Implements the Strategy Pattern. Each LLM interface (ChatGPT, Gemini, Claude) gets its own isolated DOM-parsing logic to protect the core observer from brittle CSS selectors.
- **`communication.js`**: Payload wrapper for standardizing Chrome messages.
- **`storage.js`**: Config wrapper for Chrome storage.

## Installation

1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** (toggle in the top right corner).
4. Click **Load unpacked**.
5. Select the `frontend/extension/` folder.

## Usage
- Click the **ContextOS** icon in the extensions toolbar to open the Popup.
- Verify it is "Enabled".
- Ensure the **Backend URL** matches your active ContextOS backend (e.g., `http://127.0.0.1:8000`).
- Open [ChatGPT](https://chatgpt.com), [Gemini](https://gemini.google.com), or [Claude](https://claude.ai).
- Type a prompt and hit **Send**. 
- Right-click the extension icon -> "Inspect popup" or go to the Extensions page and click "service worker" on the ContextOS card to view the Background Console logs verifying capture!

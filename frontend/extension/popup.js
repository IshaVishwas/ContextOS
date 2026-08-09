document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("enableToggle");
  const statusText = document.getElementById("statusText");
  const backendUrlInput = document.getElementById("backendUrl");
  const saveBtn = document.getElementById("saveBtn");
  const providerStatus = document.getElementById("providerStatus");
  const authEmailInput = document.getElementById("authEmail");
  const authPasswordInput = document.getElementById("authPassword");
  const loginBtn = document.getElementById("loginBtn");
  const registerBtn = document.getElementById("registerBtn");
  const authStatusMsg = document.getElementById("authStatusMsg");

  // Load saved configuration
  const loadData = () => {
    chrome.storage.local.get([
      "enabled", 
      "backendUrl", 
      "provider", 
      "connectionStatus", 
      "apiResponseTime",
      "lastRequestTime",
      "lastResponseTime",
      "lastEvalData",
      "lastOriginalPrompt",
      "lastOptimizedPrompt",
      "jwtToken",
      "authEmail"
    ], (res) => {
      toggle.checked = res.enabled !== false; // Default to true
      statusText.innerText = toggle.checked ? "Enabled" : "Disabled";
      
      if (res.backendUrl) {
        backendUrlInput.value = res.backendUrl;
      }
      
      if (res.provider) {
        providerStatus.innerText = res.provider;
      } else {
        providerStatus.innerText = "No active chat detected";
      }

      if (res.authEmail) {
        authEmailInput.value = res.authEmail;
      }

      if (res.jwtToken) {
        authStatusMsg.innerText = `Logged in as ${res.authEmail || "user"}`;
        authStatusMsg.style.color = "#10b981"; // Green
      } else {
        authStatusMsg.innerText = "Not logged in (Auto-login enabled)";
        authStatusMsg.style.color = "#a1a1aa";
      }

      document.getElementById("connStatus").innerText = res.connectionStatus || "Unknown";
      document.getElementById("respTime").innerText = res.apiResponseTime ? res.apiResponseTime + "ms" : "N/A";
      
      const formatTime = (isoString) => isoString ? new Date(isoString).toLocaleTimeString() : "N/A";
      document.getElementById("lastReq").innerText = formatTime(res.lastRequestTime);
      document.getElementById("lastRes").innerText = formatTime(res.lastResponseTime);

      // Populate Optimization Dashboard
      const dashboard = document.getElementById("evalDashboard");
      if (res.lastEvalData && res.lastEvalData.evaluation_run) {
        dashboard.style.display = "block";
        const ev = res.lastEvalData.evaluation_run;
        
        document.getElementById("compressionRatio").innerText = ev.compression_ratio ? (ev.compression_ratio * 100).toFixed(1) + "%" : "0%";
        document.getElementById("tokensSaved").innerText = ev.token_saved || 0;
        document.getElementById("evalLatency").innerText = ev.total_latency ? Math.round(ev.total_latency * 1000) + "ms" : "0ms";
        document.getElementById("evalMemories").innerText = ev.selected_memories || 0;

        document.getElementById("origTokens").innerText = ev.original_tokens || 0;
        document.getElementById("compTokens").innerText = ev.compressed_tokens || 0;

        document.getElementById("origPromptText").innerText = res.lastOriginalPrompt || "N/A";
        document.getElementById("optPromptText").innerText = res.lastOptimizedPrompt || "N/A";
      } else {
        dashboard.style.display = "none";
      }
    });
  };

  loadData();

  document.getElementById("refreshBtn").addEventListener("click", () => {
    document.getElementById("connStatus").innerText = "Checking...";
    chrome.runtime.sendMessage({ type: "CHECK_HEALTH" }, () => {
      loadData();
    });
  });

  loginBtn.addEventListener("click", () => {
    const email = authEmailInput.value.trim();
    const password = authPasswordInput.value;
    if (!email || !password) {
      authStatusMsg.innerText = "Email and password required";
      authStatusMsg.style.color = "#ef4444";
      return;
    }
    authStatusMsg.innerText = "Authenticating...";
    authStatusMsg.style.color = "#f59e0b";

    chrome.runtime.sendMessage({ type: "LOGIN", email, password }, (res) => {
      if (res && res.success) {
        authStatusMsg.innerText = `Logged in as ${email}`;
        authStatusMsg.style.color = "#10b981";
      } else {
        authStatusMsg.innerText = (res && res.error) ? res.error : "Login failed";
        authStatusMsg.style.color = "#ef4444";
      }
    });
  });

  registerBtn.addEventListener("click", () => {
    const email = authEmailInput.value.trim();
    const password = authPasswordInput.value;
    if (!email || !password) {
      authStatusMsg.innerText = "Email and password required";
      authStatusMsg.style.color = "#ef4444";
      return;
    }
    authStatusMsg.innerText = "Registering...";
    authStatusMsg.style.color = "#f59e0b";

    chrome.runtime.sendMessage({ type: "REGISTER", email, password }, (res) => {
      if (res && res.success) {
        authStatusMsg.innerText = `Registered & Logged in as ${email}`;
        authStatusMsg.style.color = "#10b981";
      } else {
        authStatusMsg.innerText = (res && res.error) ? res.error : "Registration failed";
        authStatusMsg.style.color = "#ef4444";
      }
    });
  });

  document.getElementById("copyOrigBtn").addEventListener("click", () => {
    const txt = document.getElementById("origPromptText").innerText;
    navigator.clipboard.writeText(txt);
    document.getElementById("copyOrigBtn").innerText = "Copied!";
    setTimeout(() => document.getElementById("copyOrigBtn").innerText = "Copy", 1500);
  });

  document.getElementById("copyOptBtn").addEventListener("click", () => {
    const txt = document.getElementById("optPromptText").innerText;
    navigator.clipboard.writeText(txt);
    document.getElementById("copyOptBtn").innerText = "Copied!";
    setTimeout(() => document.getElementById("copyOptBtn").innerText = "Copy", 1500);
  });

  // Handle toggle change
  toggle.addEventListener("change", () => {
    const isEnabled = toggle.checked;
    statusText.innerText = isEnabled ? "Enabled" : "Disabled";
    chrome.storage.local.set({ enabled: isEnabled });
  });

  // Handle save button
  saveBtn.addEventListener("click", () => {
    const url = backendUrlInput.value.trim();
    chrome.storage.local.set({ backendUrl: url }, () => {
      saveBtn.innerText = "Saved!";
      setTimeout(() => { saveBtn.innerText = "Save"; }, 1500);
    });
  });
  
  // Ask active tab for its provider type
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    const activeTab = tabs[0];
    if (activeTab && activeTab.url) {
      const url = activeTab.url;
      let provider = "None";
      if (url.includes("chatgpt.com") || url.includes("chat.openai.com")) provider = "ChatGPT";
      else if (url.includes("gemini.google.com")) provider = "Gemini";
      else if (url.includes("claude.ai")) provider = "Claude";
      
      providerStatus.innerText = provider;
      chrome.storage.local.set({ provider });
    }
  });
});

const PROVIDER_MAP = {
  "ChatGPT": "openai",
  "Gemini": "gemini",
  "Claude": "anthropic"
};

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "PROMPT_CAPTURED") {
    console.log("[ContextOS] background received PROMPT_CAPTURED", request.payload);
    
    processPayload(request.payload).then((res) => {
       console.log("[ContextOS] Backend process complete", res);
    });

    sendResponse({ status: "processing", received: true });
    return true; // Keep channel open for async response
  } else if (request.type === "CHECK_HEALTH") {
    checkHealth().then((res) => {
      sendResponse(res);
    });
    return true;
  } else if (request.type === "LOGIN") {
    handleLogin(request.email, request.password).then((res) => {
      sendResponse(res);
    });
    return true;
  } else if (request.type === "REGISTER") {
    handleRegister(request.email, request.password).then((res) => {
      sendResponse(res);
    });
    return true;
  }
});

async function checkHealth() {
  try {
    const data = await chrome.storage.local.get(["backendUrl"]);
    const backendUrl = data.backendUrl || "http://127.0.0.1:8000";

    const startTime = performance.now();
    const response = await fetch(`${backendUrl}/api/v1/evaluation/stats`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });
    const endTime = performance.now();
    const responseTime = Math.round(endTime - startTime);

    if (response.ok) {
      await chrome.storage.local.set({
        connectionStatus: "Connected",
        apiResponseTime: responseTime,
        lastResponseTime: new Date().toISOString()
      });
      return { status: "Connected", responseTime: responseTime };
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error("[ContextOS] Health check failed:", error);
    await chrome.storage.local.set({
      connectionStatus: "Backend Offline / Connection Refused",
      apiResponseTime: null
    });
    return { status: "Backend Offline / Connection Refused", responseTime: null };
  }
}

async function getOrFetchToken(backendUrl) {
  const store = await chrome.storage.local.get(["jwtToken", "authEmail", "authPassword"]);
  if (store.jwtToken) {
    return store.jwtToken;
  }

  // Fallback auto-authentication for seamless local extension usage
  const email = store.authEmail || "ext_user@contextos.ai";
  const password = store.authPassword || "password123";

  // Try login first
  let token = await attemptLogin(backendUrl, email, password);
  if (!token) {
    // If login failed, register then login
    await attemptRegister(backendUrl, email, password);
    token = await attemptLogin(backendUrl, email, password);
  }

  if (token) {
    await chrome.storage.local.set({ jwtToken: token, authEmail: email });
  }
  return token;
}

async function attemptLogin(backendUrl, email, password) {
  try {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${backendUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData
    });

    if (res.ok) {
      const data = await res.json();
      return data.access_token;
    }
  } catch (e) {
    console.error("[ContextOS] Login attempt failed:", e);
  }
  return null;
}

async function attemptRegister(backendUrl, email, password) {
  try {
    await fetch(`${backendUrl}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password })
    });
  } catch (e) {
    console.error("[ContextOS] Register attempt failed:", e);
  }
}

async function getOrCreateConversation(backendUrl, token) {
  const store = await chrome.storage.local.get(["activeConversationId"]);
  if (store.activeConversationId) {
    return store.activeConversationId;
  }

  try {
    const res = await fetch(`${backendUrl}/api/v1/conversations/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ title: "Gemini ContextOS Session" })
    });

    if (res.ok) {
      const data = await res.json();
      await chrome.storage.local.set({ activeConversationId: data.id });
      return data.id;
    }
  } catch (e) {
    console.error("[ContextOS] Failed to create conversation:", e);
  }
  return 1; // Fallback ID
}

async function handleLogin(email, password) {
  const data = await chrome.storage.local.get(["backendUrl"]);
  const backendUrl = data.backendUrl || "http://127.0.0.1:8000";
  const token = await attemptLogin(backendUrl, email, password);
  if (token) {
    await chrome.storage.local.set({ jwtToken: token, authEmail: email, authPassword: password });
    return { success: true, email };
  } else {
    return { success: false, error: "Invalid email or password" };
  }
}

async function handleRegister(email, password) {
  const data = await chrome.storage.local.get(["backendUrl"]);
  const backendUrl = data.backendUrl || "http://127.0.0.1:8000";
  await attemptRegister(backendUrl, email, password);
  return await handleLogin(email, password);
}

async function processPayload(payload) {
  try {
    const data = await chrome.storage.local.get(["backendUrl", "enabled"]);
    if (data.enabled === false) {
      console.log("[ContextOS] Extension is disabled. Aborting.");
      return;
    }

    const backendUrl = data.backendUrl || "http://127.0.0.1:8000";
    const mappedProvider = PROVIDER_MAP[payload.provider] || "gemini";

    // Obtain valid JWT Token
    const jwtToken = await getOrFetchToken(backendUrl);
    if (!jwtToken) {
      throw new Error("HTTP error! status: 401 Unauthorized (No JWT token)");
    }

    // Obtain valid conversation ID for this user
    let conversationId = await getOrCreateConversation(backendUrl, jwtToken);

    console.log("[ContextOS] Backend request starting");
    const startTime = performance.now();
    
    await chrome.storage.local.set({ 
      connectionStatus: "Connecting...",
      lastRequestTime: new Date().toISOString()
    });

    const requestBody = {
      provider: mappedProvider,
      conversation_id: conversationId,
      query: payload.prompt
    };

    let response = await fetch(`${backendUrl}/api/v1/llm/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${jwtToken}`
      },
      body: JSON.stringify(requestBody)
    });

    console.log(`[ContextOS] Backend response status: ${response.status}`);

    // If conversation not found (e.g. database reset), recreate conversation and retry once
    if (response.status === 404 || response.status === 403) {
      await chrome.storage.local.remove(["activeConversationId"]);
      conversationId = await getOrCreateConversation(backendUrl, jwtToken);
      requestBody.conversation_id = conversationId;
      response = await fetch(`${backendUrl}/api/v1/llm/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${jwtToken}`
        },
        body: JSON.stringify(requestBody)
      });
      console.log(`[ContextOS] Backend retry response status: ${response.status}`);
    }

    const endTime = performance.now();
    const responseTime = Math.round(endTime - startTime);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("[ContextOS] Optimized Response Received:", result);

    let evalData = null;
    if (result.evaluation_id) {
      try {
        const evalRes = await fetch(`${backendUrl}/api/v1/evaluation/${result.evaluation_id}`, {
          headers: { "Authorization": `Bearer ${jwtToken}` }
        });
        if (evalRes.ok) {
          evalData = await evalRes.json();
        }
      } catch (e) {
        console.error("[ContextOS] Failed to fetch evaluation data", e);
      }
    }

    await chrome.storage.local.set({
      connectionStatus: "Connected",
      apiResponseTime: responseTime,
      lastResponseTime: new Date().toISOString(),
      lastEvalData: evalData ? { evaluation_run: evalData } : null,
      lastOriginalPrompt: payload.prompt,
      lastOptimizedPrompt: result.optimized_prompt || "No optimized prompt returned."
    });

    return result;
  } catch (error) {
    console.error("[ContextOS] Backend connection failed:", error);
    let statusText = "Connection Failed";
    if (error.message.includes("Failed to fetch")) {
      statusText = "Backend Offline / Connection Refused";
    } else if (error.message.includes("HTTP error")) {
      statusText = `Backend Error: ${error.message}`;
    }

    await chrome.storage.local.set({
      connectionStatus: statusText,
      apiResponseTime: null
    });
  }
}

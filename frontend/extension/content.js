// Bootstrap the content script
(async () => {
  console.log("[ContextOS] Gemini content script loaded");
  
  // 1. Identify current provider
  const url = window.location.href;
  let strategy = null;
  
  if (url.includes("chatgpt.com") || url.includes("chat.openai.com")) {
    strategy = new window.ChatGPTStrategy();
  } else if (url.includes("gemini.google.com")) {
    strategy = new window.GeminiStrategy();
  } else if (url.includes("claude.ai")) {
    strategy = new window.ClaudeStrategy();
  }

  // 2. Initialize observer if strategy exists
  if (strategy) {
    console.log(`[ContextOS] Provider detected: ${strategy.name}`);
    
    // Store provider for popup UI
    await window.ContextStorage.set("provider", strategy.name);
    
    // Start observing DOM events
    new window.ContextObserver(strategy);
  } else {
    console.log("[ContextOS] No supported provider found on this page.");
  }
})();

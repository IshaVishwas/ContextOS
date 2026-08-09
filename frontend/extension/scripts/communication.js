class ContextCommunication {
  static async dispatchPrompt(payload) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({
        type: "PROMPT_CAPTURED",
        payload: payload
      }, (response) => {
        if (chrome.runtime.lastError) {
          console.error("[ContextOS] Communication Error:", chrome.runtime.lastError);
          resolve(null);
        } else {
          resolve(response);
        }
      });
    });
  }
}

window.ContextCommunication = ContextCommunication;

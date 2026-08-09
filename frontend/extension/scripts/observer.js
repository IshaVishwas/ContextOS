class ContextObserver {
  constructor(strategy) {
    this.strategy = strategy;
    this.setupListeners();
  }

  setupListeners() {
    // Listen for Enter key presses (handle Shift+Enter gracefully)
    document.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        this.handleCapture(e);
      }
    }, true); // Capture phase to get it before React/Angular clears it

    // Listen for Clicks on submit buttons
    document.addEventListener("click", (e) => {
      const button = e.target.closest('button');
      if (button) {
        const ariaLabel = (button.getAttribute('aria-label') || '').toLowerCase();
        const dataTestId = (button.getAttribute('data-testid') || '').toLowerCase();
        
        if (ariaLabel.includes('send') || ariaLabel.includes('submit') || dataTestId.includes('send') || button.querySelector('svg')) {
           this.handleCapture(e);
        }
      }
    }, true);
  }

  async handleCapture(event) {
    const isEnabled = await window.ContextStorage.isEnabled();
    if (!isEnabled) return;

    const promptText = this.strategy.extractPrompt(event);
    
    if (promptText && promptText.length > 0) {
      console.log("[ContextOS] Gemini prompt detected:", promptText);
      
      const payload = {
        prompt: promptText,
        provider: this.strategy.name,
        url: window.location.href,
        timestamp: new Date().toISOString()
      };
      
      console.log("[ContextOS] PROMPT_CAPTURED sent");
      // Dispatch the payload to background service worker
      window.ContextCommunication.dispatchPrompt(payload);
    }
  }
}

window.ContextObserver = ContextObserver;

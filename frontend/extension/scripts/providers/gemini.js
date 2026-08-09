class GeminiStrategy extends window.ProviderStrategy {
  constructor() {
    super("Gemini");
  }

  extractPrompt() {
    // Robust selectors matching Gemini's rich-textarea contenteditable elements
    const selectors = [
      'rich-textarea div[contenteditable="true"]',
      'div[contenteditable="true"][aria-label*="Gemini"]',
      'div[contenteditable="true"][role="textbox"]',
      'div[contenteditable="true"]',
      '.ql-editor',
      'textarea'
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) {
        const txt = this.getTextFromElement(el);
        if (txt && txt.length > 0) {
          return txt;
        }
      }
    }
    return "";
  }
}

window.GeminiStrategy = GeminiStrategy;

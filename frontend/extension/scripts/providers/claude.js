class ClaudeStrategy extends window.ProviderStrategy {
  constructor() {
    super("Claude");
  }

  extractPrompt() {
    // Claude typically uses a contenteditable div with specific classes
    const editor = document.querySelector('div[contenteditable="true"].ProseMirror');
    return this.getTextFromElement(editor);
  }
}

window.ClaudeStrategy = ClaudeStrategy;

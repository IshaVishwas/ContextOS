class ChatGPTStrategy extends window.ProviderStrategy {
  constructor() {
    super("ChatGPT");
  }

  extractPrompt() {
    // ChatGPT typically uses a textarea with id 'prompt-textarea'
    const textarea = document.getElementById('prompt-textarea');
    return this.getTextFromElement(textarea);
  }
}

window.ChatGPTStrategy = ChatGPTStrategy;

class ProviderStrategy {
  constructor(name) {
    this.name = name;
  }

  // To be overridden by subclasses
  // Returns the text string of the prompt being submitted
  extractPrompt() {
    throw new Error("extractPrompt() must be implemented by subclass");
  }

  // Common utility to get text from a contenteditable or textarea
  getTextFromElement(element) {
    if (!element) return "";
    if (element.tagName === "TEXTAREA" || element.tagName === "INPUT") {
      return element.value.trim();
    }
    return element.innerText.trim();
  }
}

window.ProviderStrategy = ProviderStrategy;

// Abstraction over chrome.storage.local
class ContextStorage {
  static async get(key) {
    return new Promise((resolve) => {
      chrome.storage.local.get([key], (result) => {
        resolve(result[key]);
      });
    });
  }

  static async set(key, value) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [key]: value }, resolve);
    });
  }

  static async isEnabled() {
    const enabled = await this.get("enabled");
    return enabled !== false; // Default true
  }
}

// Attach to window for modular usage if not using ES modules
window.ContextStorage = ContextStorage;

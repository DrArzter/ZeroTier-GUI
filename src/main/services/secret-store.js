'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');

class SecretStore {
  constructor({ safeStorage, userDataPath }) {
    this.safeStorage = safeStorage;
    this.filePath = path.join(userDataPath, 'credentials.bin');
    this.sessionToken = null;
  }

  getBackend() {
    if (!this.safeStorage.isEncryptionAvailable()) return 'memory';
    if (process.platform !== 'linux') return 'encrypted';

    const backend = this.safeStorage.getSelectedStorageBackend?.();
    return backend && backend !== 'basic_text' ? backend : 'memory';
  }

  canPersist() {
    return this.getBackend() !== 'memory';
  }

  async getToken() {
    if (this.sessionToken) return this.sessionToken;
    if (!this.canPersist()) return null;

    try {
      const encrypted = await fs.readFile(this.filePath);
      return this.safeStorage.decryptString(encrypted);
    } catch (error) {
      if (error.code === 'ENOENT') return null;
      await this.clear();
      return null;
    }
  }

  async setToken(token, persist = true) {
    this.sessionToken = token;
    if (!persist || !this.canPersist()) {
      await fs.rm(this.filePath, { force: true });
      return { persisted: false, backend: this.getBackend() };
    }

    const encrypted = this.safeStorage.encryptString(token);
    await fs.mkdir(path.dirname(this.filePath), { recursive: true });
    await fs.writeFile(this.filePath, encrypted, { mode: 0o600 });
    return { persisted: true, backend: this.getBackend() };
  }

  async clear() {
    this.sessionToken = null;
    await fs.rm(this.filePath, { force: true });
  }

  async getStatus() {
    return {
      configured: Boolean(await this.getToken()),
      canPersist: this.canPersist(),
      backend: this.getBackend(),
    };
  }
}

module.exports = { SecretStore };

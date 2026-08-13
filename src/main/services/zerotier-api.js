'use strict';

class ZeroTierApi {
  constructor({ getToken, fetchImpl = globalThis.fetch }) {
    this.getToken = getToken;
    this.fetch = fetchImpl;
    this.baseUrl = 'https://api.zerotier.com/api/v1';
  }

  async request(pathname, options = {}, tokenOverride = null) {
    const token = tokenOverride || await this.getToken();
    if (!token) throw new Error('ZeroTier API token is not configured.');

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15_000);

    try {
      const response = await this.fetch(`${this.baseUrl}${pathname}`, {
        ...options,
        headers: {
          Accept: 'application/json',
          Authorization: `Bearer ${token}`,
          ...(options.body ? { 'Content-Type': 'application/json' } : {}),
          ...options.headers,
        },
        signal: controller.signal,
      });

      const text = await response.text();
      let data = null;
      if (text) {
        try {
          data = JSON.parse(text);
        } catch {
          data = text;
        }
      }

      if (!response.ok) {
        const detail = data?.message || data?.error || response.statusText;
        throw new Error(`ZeroTier API ${response.status}: ${detail}`);
      }
      return data;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('ZeroTier API request timed out.');
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  getStatus() {
    return this.request('/status');
  }

  validateToken(token) {
    return this.request('/status', {}, token);
  }

  getNetworks() {
    return this.request('/network');
  }

  getNetwork(networkId) {
    return this.request(`/network/${networkId}`);
  }

  getMembers(networkId) {
    return this.request(`/network/${networkId}/member`);
  }

  updateNetwork(networkId, data) {
    return this.request(`/network/${networkId}`, { method: 'POST', body: JSON.stringify(data) });
  }

  updateMember(networkId, memberId, data) {
    return this.request(`/network/${networkId}/member/${memberId}`, { method: 'POST', body: JSON.stringify(data) });
  }

  createNetwork() {
    return this.request('/network', { method: 'POST', body: '{}' });
  }

  deleteNetwork(networkId) {
    return this.request(`/network/${networkId}`, { method: 'DELETE' });
  }

  deleteMember(networkId, memberId) {
    return this.request(`/network/${networkId}/member/${memberId}`, { method: 'DELETE' });
  }
}

module.exports = { ZeroTierApi };

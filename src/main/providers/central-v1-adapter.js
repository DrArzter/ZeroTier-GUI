'use strict';

class CentralV1Adapter {
  constructor({ client }) {
    if (!client) throw new TypeError('A Legacy Central API client is required.');
    this.client = client;
    this.descriptor = Object.freeze({ kind: 'central', implementation: 'legacy-v1', apiVersion: 1 });
  }

  validateCredential(token) { return this.client.validateToken(token); }
  getStatus() { return this.client.getStatus(); }
  getNetworks() { return this.client.getNetworks(); }
  getNetwork(networkId) { return this.client.getNetwork(networkId); }
  getMembers(networkId) { return this.client.getMembers(networkId); }
  updateNetwork(networkId, data) { return this.client.updateNetwork(networkId, data); }
  updateMember(networkId, memberId, data) { return this.client.updateMember(networkId, memberId, data); }
  createNetwork() { return this.client.createNetwork(); }
  deleteNetwork(networkId) { return this.client.deleteNetwork(networkId); }
  deleteMember(networkId, memberId) { return this.client.deleteMember(networkId, memberId); }
}

module.exports = { CentralV1Adapter };

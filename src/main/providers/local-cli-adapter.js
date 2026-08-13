'use strict';

class LocalCliAdapter {
  constructor({ client }) {
    if (!client) throw new TypeError('A zerotier-cli client is required.');
    this.client = client;
    this.descriptor = Object.freeze({ kind: 'local', implementation: 'zerotier-cli' });
  }

  getStatus() { return this.client.getStatus(); }
  getAccessStatus() { return this.client.getAccessStatus(); }
  repairAccess() { return this.client.repairAccess(); }
  getNetworks() { return this.client.getNetworks(); }
  join(networkId) { return this.client.join(networkId); }
  leave(networkId) { return this.client.leave(networkId); }
  setNetworkSetting(networkId, setting, enabled) { return this.client.setNetworkSetting(networkId, setting, enabled); }
  ping(address) { return this.client.ping(address); }
}

module.exports = { LocalCliAdapter };

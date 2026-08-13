'use strict';

const { assertCentralProvider, assertLocalProvider } = require('./provider-contracts');

class ProviderStrategy {
  constructor({ central = {}, local = {} } = {}) {
    this.centralFactories = new Map(Object.entries(central));
    this.localFactories = new Map(Object.entries(local));
  }

  select({ central = 'legacy-v1', local = 'zerotier-cli' } = {}) {
    const centralFactory = this.centralFactories.get(central);
    const localFactory = this.localFactories.get(local);
    if (!centralFactory) throw new Error(`Unsupported Central provider: ${central}`);
    if (!localFactory) throw new Error(`Unsupported local provider: ${local}`);
    return Object.freeze({
      central: assertCentralProvider(centralFactory()),
      local: assertLocalProvider(localFactory()),
    });
  }
}

module.exports = { ProviderStrategy };

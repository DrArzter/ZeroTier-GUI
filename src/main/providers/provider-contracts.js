'use strict';

const CENTRAL_METHODS = Object.freeze([
  'validateCredential', 'getStatus', 'getNetworks', 'getNetwork', 'getMembers',
  'updateNetwork', 'updateMember', 'createNetwork', 'deleteNetwork', 'deleteMember',
]);

const LOCAL_METHODS = Object.freeze([
  'getStatus', 'getAccessStatus', 'repairAccess', 'getNetworks',
  'join', 'leave', 'setNetworkSetting', 'ping',
]);

function assertProvider(provider, kind, methods) {
  if (!provider || typeof provider !== 'object') throw new TypeError(`${kind} provider is required.`);
  for (const method of methods) {
    if (typeof provider[method] !== 'function') throw new TypeError(`${kind} provider must implement ${method}().`);
  }
  return provider;
}

const assertCentralProvider = (provider) => assertProvider(provider, 'Central', CENTRAL_METHODS);
const assertLocalProvider = (provider) => assertProvider(provider, 'Local', LOCAL_METHODS);

module.exports = { CENTRAL_METHODS, LOCAL_METHODS, assertCentralProvider, assertLocalProvider };

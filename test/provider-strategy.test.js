'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { CENTRAL_METHODS, LOCAL_METHODS } = require('../src/main/providers/provider-contracts');
const { ProviderStrategy } = require('../src/main/providers/provider-strategy');

const providerWith = (methods, marker) => Object.fromEntries([
  ['marker', marker],
  ...methods.map((method) => [method, () => null]),
]);

test('selects configured Central and local implementations', () => {
  const strategy = new ProviderStrategy({
    central: { 'legacy-v1': () => providerWith(CENTRAL_METHODS, 'central-v1') },
    local: { 'zerotier-cli': () => providerWith(LOCAL_METHODS, 'cli') },
  });
  const selected = strategy.select();
  assert.equal(selected.central.marker, 'central-v1');
  assert.equal(selected.local.marker, 'cli');
});

test('rejects unknown or incomplete providers early', () => {
  const strategy = new ProviderStrategy({
    central: { broken: () => ({}) },
    local: { 'zerotier-cli': () => providerWith(LOCAL_METHODS, 'cli') },
  });
  assert.throws(() => strategy.select({ central: 'missing' }), /Unsupported Central provider/);
  assert.throws(() => strategy.select({ central: 'broken' }), /must implement validateCredential/);
});

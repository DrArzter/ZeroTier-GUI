'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { requireMemberId, requireNetworkId, requireToken } = require('../src/shared/validation');

test('normalizes valid ZeroTier IDs', () => {
  assert.equal(requireNetworkId(' ABCDEF0123456789 '), 'abcdef0123456789');
  assert.equal(requireMemberId(' A1B2C3D4E5 '), 'a1b2c3d4e5');
});

test('rejects malformed ZeroTier IDs', () => {
  assert.throws(() => requireNetworkId('1234'));
  assert.throws(() => requireNetworkId('gggggggggggggggg'));
  assert.throws(() => requireMemberId('../bad-id'));
});

test('accepts an opaque token but rejects whitespace and short values', () => {
  assert.equal(requireToken('abcdefghijklmnop'), 'abcdefghijklmnop');
  assert.throws(() => requireToken('too-short'));
  assert.throws(() => requireToken('abcdefghijkl mno'));
});

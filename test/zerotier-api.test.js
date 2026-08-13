'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { ZeroTierApi } = require('../src/main/services/zerotier-api');

test('adds the bearer token and returns JSON', async () => {
  let request;
  const client = new ZeroTierApi({
    getToken: async () => 'secret-token-value',
    fetchImpl: async (url, options) => {
      request = { url, options };
      return new Response(JSON.stringify([{ id: 'abcdef0123456789' }]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    },
  });

  const result = await client.getNetworks();
  assert.equal(request.url, 'https://api.zerotier.com/api/v1/network');
  assert.equal(request.options.headers.Authorization, 'Bearer secret-token-value');
  assert.equal(result[0].id, 'abcdef0123456789');
});

test('reports useful API errors without exposing the token', async () => {
  const client = new ZeroTierApi({
    getToken: async () => 'secret-token-value',
    fetchImpl: async () => new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
  });

  await assert.rejects(() => client.getStatus(), /ZeroTier API 401: Unauthorized/);
});

test('can validate a candidate without replacing the stored token', async () => {
  let authorization;
  const client = new ZeroTierApi({
    getToken: async () => 'stored-token-value',
    fetchImpl: async (_url, options) => {
      authorization = options.headers.Authorization;
      return new Response('{}', { status: 200 });
    },
  });

  await client.validateToken('candidate-token-value');
  assert.equal(authorization, 'Bearer candidate-token-value');
});

test('updates members and networks with JSON POST requests', async () => {
  const requests = [];
  const client = new ZeroTierApi({
    getToken: async () => 'secret-token-value',
    fetchImpl: async (url, options) => {
      requests.push({ url, options });
      return new Response('{}', { status: 200 });
    },
  });

  await client.updateNetwork('abcdef0123456789', { config: { name: 'Office' } });
  await client.updateMember('abcdef0123456789', 'a1b2c3d4e5', { config: { authorized: true } });
  assert.equal(requests[0].options.method, 'POST');
  assert.deepEqual(JSON.parse(requests[0].options.body), { config: { name: 'Office' } });
  assert.equal(requests[1].url, 'https://api.zerotier.com/api/v1/network/abcdef0123456789/member/a1b2c3d4e5');
  assert.deepEqual(JSON.parse(requests[1].options.body), { config: { authorized: true } });
});

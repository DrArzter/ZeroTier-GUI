'use strict';

const NETWORK_ID_PATTERN = /^[0-9a-f]{16}$/i;
const MEMBER_ID_PATTERN = /^[0-9a-f]{10}$/i;

function requireNetworkId(value) {
  const id = String(value ?? '').trim();
  if (!NETWORK_ID_PATTERN.test(id)) {
    throw new Error('Network ID must contain exactly 16 hexadecimal characters.');
  }
  return id.toLowerCase();
}

function requireMemberId(value) {
  const id = String(value ?? '').trim();
  if (!MEMBER_ID_PATTERN.test(id)) {
    throw new Error('Member ID must contain exactly 10 hexadecimal characters.');
  }
  return id.toLowerCase();
}

function requireToken(value) {
  const token = String(value ?? '').trim();
  if (token.length < 16 || token.length > 512 || /\s/.test(token)) {
    throw new Error('The API token has an invalid format.');
  }
  return token;
}

module.exports = {
  requireMemberId,
  requireNetworkId,
  requireToken,
};

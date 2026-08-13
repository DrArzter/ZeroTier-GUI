'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { parsePingOutput } = require('../src/main/services/zerotier-cli');

test('parses Linux ping metrics into structured data', () => {
  const result = parsePingOutput('172.29.232.148', `PING 172.29.232.148 (172.29.232.148) 56(84) bytes of data.\n64 bytes from 172.29.232.148: icmp_seq=1 ttl=127 time=26.5 ms\n\n--- 172.29.232.148 ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 26.509/26.509/26.509/0.000 ms`);
  assert.equal(result.success, true);
  assert.equal(result.packetsReceived, 1);
  assert.equal(result.packetLossPercent, 0);
  assert.equal(result.latencyMs, 26.509);
});

test('returns an understandable failed result when no packets reply', () => {
  const result = parsePingOutput('10.0.0.2', '1 packets transmitted, 0 received, 100% packet loss', 'Host did not reply.');
  assert.equal(result.success, false);
  assert.equal(result.packetLossPercent, 100);
  assert.equal(result.error, 'Host did not reply.');
});

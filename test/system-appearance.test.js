'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { normalizeHexAccent, parseKdeColor, parsePortalAccent } = require('../src/main/services/system-appearance');

test('parses an XDG portal accent tuple', () => {
  assert.equal(parsePortalAccent('(<(0.274509817, 0.274509817, 0.545098066)>,)'), '#46468b');
  assert.equal(parsePortalAccent('(missing,)'), null);
});

test('normalizes Electron RGBA accent colors to CSS RGB', () => {
  assert.equal(normalizeHexAccent('aabbccdd'), '#aabbcc');
  assert.equal(normalizeHexAccent('#112233'), '#112233');
  assert.equal(normalizeHexAccent('invalid'), null);
});

test('parses KDE RGB color values', () => {
  assert.equal(parseKdeColor('176,97,96\n'), '#b06160');
  assert.equal(parseKdeColor('223,223,223,100'), '#dfdfdf64');
  assert.equal(parseKdeColor('999,0,0'), null);
  assert.equal(parseKdeColor('red'), null);
});

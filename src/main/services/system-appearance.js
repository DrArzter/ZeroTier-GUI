'use strict';

const { execFile } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { promisify } = require('node:util');

const execFileAsync = promisify(execFile);

function channelToHex(value) {
  return Math.round(Math.max(0, Math.min(1, Number(value))) * 255).toString(16).padStart(2, '0');
}

function parsePortalAccent(output) {
  const match = String(output).match(/\(\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*,\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*,\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*\)/);
  if (!match) return null;
  return `#${channelToHex(match[1])}${channelToHex(match[2])}${channelToHex(match[3])}`;
}

function normalizeHexAccent(value) {
  const hex = String(value || '').replace(/^#/, '');
  return /^[0-9a-f]{6,8}$/i.test(hex) ? `#${hex.slice(0, 6)}` : null;
}

function parseKdeColor(value) {
  const parts = String(value || '').trim().split(',').map(Number);
  if (![3, 4].includes(parts.length) || parts.some((part) => !Number.isInteger(part) || part < 0 || part > 255)) return null;
  return `#${parts.map((part) => part.toString(16).padStart(2, '0')).join('')}`;
}

class SystemAppearance {
  constructor({ nativeTheme, systemPreferences }) {
    this.nativeTheme = nativeTheme;
    this.systemPreferences = systemPreferences;
  }

  getPlatformStyle() {
    if (process.platform === 'win32') return 'windows';
    if (process.platform === 'darwin') return 'macos';
    const desktop = `${process.env.XDG_CURRENT_DESKTOP || ''}:${process.env.XDG_SESSION_DESKTOP || ''}`.toLowerCase();
    if (desktop.includes('kde') || desktop.includes('plasma')) return 'kde';
    return 'linux';
  }

  async getLinuxPortalAccent() {
    try {
      const { stdout } = await execFileAsync('gdbus', [
        'call', '--session', '--dest', 'org.freedesktop.portal.Desktop',
        '--object-path', '/org/freedesktop/portal/desktop',
        '--method', 'org.freedesktop.portal.Settings.ReadOne',
        'org.freedesktop.appearance', 'accent-color',
      ], { encoding: 'utf8', timeout: 1_500, windowsHide: true });
      return parsePortalAccent(stdout);
    } catch { return null; }
  }

  async readKdeValue(file, group, key) {
    for (const executable of ['kreadconfig6', 'kreadconfig5']) {
      try {
        const { stdout } = await execFileAsync(executable, [
          '--file', file, '--group', group, '--key', key,
        ], { encoding: 'utf8', timeout: 1_000, windowsHide: true });
        const value = stdout.trim();
        if (value) return value;
      } catch (error) {
        if (error.code !== 'ENOENT') continue;
      }
    }
    return null;
  }

  async getKdeAccent() {
    for (const executable of ['kreadconfig6', 'kreadconfig5']) {
      try {
        const { stdout } = await execFileAsync(executable, [
          '--file', 'kdeglobals', '--group', 'General', '--key', 'AccentColor',
        ], { encoding: 'utf8', timeout: 1_000, windowsHide: true });
        const accent = parseKdeColor(stdout);
        if (accent) return { color: accent, source: 'kde-accent' };
      } catch (error) {
        if (error.code !== 'ENOENT') continue;
      }
    }
    return { color: null, source: null };
  }

  async getKdePalette() {
    const entries = {
      windowBackground: ['Colors:Window', 'BackgroundNormal'],
      windowAlternate: ['Colors:Window', 'BackgroundAlternate'],
      windowText: ['Colors:Window', 'ForegroundNormal'],
      inactiveText: ['Colors:Window', 'ForegroundInactive'],
      viewBackground: ['Colors:View', 'BackgroundNormal'],
      viewAlternate: ['Colors:View', 'BackgroundAlternate'],
      buttonBackground: ['Colors:Button', 'BackgroundNormal'],
      buttonText: ['Colors:Button', 'ForegroundNormal'],
      negativeText: ['Colors:Window', 'ForegroundNegative'],
      positiveText: ['Colors:Window', 'ForegroundPositive'],
      selectionBackground: ['Colors:Selection', 'BackgroundNormal'],
      selectionText: ['Colors:Selection', 'ForegroundNormal'],
    };
    const pairs = await Promise.all(Object.entries(entries).map(async ([name, [group, key]]) => (
      [name, parseKdeColor(await this.readKdeValue('kdeglobals', group, key))]
    )));
    return Object.fromEntries(pairs.filter(([, value]) => value));
  }

  async getAccentColor() {
    if (process.platform === 'linux') {
      if (this.getPlatformStyle() === 'kde') {
        const kdeAccent = await this.getKdeAccent();
        if (kdeAccent.color) return kdeAccent;
      }
      return { color: await this.getLinuxPortalAccent(), source: 'xdg-portal' };
    }
    if (process.platform === 'darwin') {
      try { return { color: normalizeHexAccent(this.systemPreferences.getAccentColor()), source: 'system-preferences' }; }
      catch { return { color: null, source: null }; }
    }
    return { color: null, source: 'chromium' };
  }

  async get() {
    let reducedMotion = false;
    try { reducedMotion = Boolean(this.systemPreferences.getAnimationSettings().prefersReducedMotion); }
    catch { /* Unsupported platform. */ }
    const accent = await this.getAccentColor();
    const palette = this.getPlatformStyle() === 'kde' ? await this.getKdePalette() : null;
    return {
      platformStyle: this.getPlatformStyle(),
      colorScheme: this.nativeTheme.shouldUseDarkColors ? 'dark' : 'light',
      highContrast: Boolean(this.nativeTheme.shouldUseHighContrastColors || this.nativeTheme.inForcedColorsMode),
      reducedMotion,
      reducedTransparency: Boolean(this.nativeTheme.prefersReducedTransparency),
      accentColor: accent.color,
      accentSource: accent.source,
      palette,
    };
  }

  watch(callback) {
    if (this.getPlatformStyle() !== 'kde') return () => {};
    const configPath = path.join(os.homedir(), '.config', 'kdeglobals');
    let timer = null;
    try {
      const watcher = fs.watch(configPath, () => {
        clearTimeout(timer);
        timer = setTimeout(callback, 120);
      });
      return () => { clearTimeout(timer); watcher.close(); };
    } catch { return () => {}; }
  }
}

module.exports = { SystemAppearance, normalizeHexAccent, parseKdeColor, parsePortalAccent };

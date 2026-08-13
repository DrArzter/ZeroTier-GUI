'use strict';

const { execFile } = require('node:child_process');
const { constants: fsConstants } = require('node:fs');
const fs = require('node:fs/promises');
const os = require('node:os');
const { promisify } = require('node:util');

const execFileAsync = promisify(execFile);
const LINUX_TOKEN_PATH = '/var/lib/zerotier-one/authtoken.secret';

function parsePingOutput(address, rawOutput, fallbackError = null) {
  const raw = String(rawOutput || '').trim();
  const packets = raw.match(/(\d+)\s+packets?\s+transmitted,\s*(\d+)\s+(?:packets?\s+)?received,\s*([\d.]+)%\s+packet\s+loss/i)
    || raw.match(/Packets:\s+Sent\s*=\s*(\d+),\s*Received\s*=\s*(\d+),\s*Lost\s*=\s*\d+\s*\(([\d.]+)%\s*loss\)/i);
  const unixLatency = raw.match(/(?:rtt|round-trip)[^=]*=\s*[\d.]+\/([\d.]+)\/[\d.]+\/[\d.]+\s*ms/i);
  const windowsLatency = raw.match(/Average\s*=\s*(\d+)ms/i);
  const replyLatency = raw.match(/time[=<]\s*([\d.]+)\s*ms/i);
  const transmitted = packets ? Number(packets[1]) : null;
  const received = packets ? Number(packets[2]) : null;
  const packetLossPercent = packets ? Number(packets[3]) : null;
  const latencyMs = Number(unixLatency?.[1] ?? windowsLatency?.[1] ?? replyLatency?.[1]);
  const success = received !== null ? received > 0 : /(?:bytes from|reply from)/i.test(raw);

  return {
    address,
    success,
    packetsTransmitted: transmitted,
    packetsReceived: received,
    packetLossPercent,
    latencyMs: Number.isFinite(latencyMs) ? latencyMs : null,
    error: success ? null : fallbackError || 'No reply received.',
    raw,
  };
}

class ZeroTierCli {
  async run(args, options = {}) {
    try {
      const { stdout, stderr } = await execFileAsync('zerotier-cli', args, {
        encoding: 'utf8',
        timeout: options.timeout ?? 10_000,
        windowsHide: true,
        maxBuffer: 1024 * 1024,
      });
      return { stdout: stdout.trim(), stderr: stderr.trim() };
    } catch (error) {
      if (error.code === 'ENOENT') {
        throw new Error('zerotier-cli is not installed or is not in PATH.');
      }
      if (error.killed) throw new Error('zerotier-cli timed out.');
      const detail = String(error.stderr || error.stdout || error.message).trim();
      throw new Error(detail || 'zerotier-cli failed.');
    }
  }

  async getStatus() {
    const { stdout } = await this.run(['-j', 'info']);
    return JSON.parse(stdout);
  }

  async getNetworks() {
    const { stdout } = await this.run(['-j', 'listnetworks']);
    return JSON.parse(stdout);
  }

  async join(networkId) {
    await this.run(['join', networkId]);
    return { success: true };
  }

  async leave(networkId) {
    await this.run(['leave', networkId]);
    return { success: true };
  }

  async setNetworkSetting(networkId, setting, enabled) {
    const allowedSettings = new Set(['allowManaged', 'allowGlobal', 'allowDefault', 'allowDNS']);
    if (!allowedSettings.has(setting)) throw new Error('Unsupported local network setting.');
    await this.run(['set', networkId, `${setting}=${enabled ? '1' : '0'}`]);
    return { success: true };
  }

  async ping(address) {
    if (!/^[0-9a-f:.]+$/i.test(address)) throw new Error('Invalid IP address.');
    const args = process.platform === 'win32'
      ? ['-n', '1', '-w', '3000', address]
      : ['-c', '1', '-W', '3', address];
    try {
      const { stdout } = await execFileAsync('ping', args, {
        encoding: 'utf8',
        timeout: 5_000,
        windowsHide: true,
        maxBuffer: 256 * 1024,
      });
      return parsePingOutput(address, stdout);
    } catch (error) {
      if (error.code === 'ENOENT') throw new Error('The system ping command is not installed.');
      const raw = String(error.stdout || error.stderr || '').trim();
      if (raw) return parsePingOutput(address, raw, error.killed ? 'Ping timed out.' : 'Host did not reply.');
      throw new Error(error.killed ? 'Ping timed out.' : String(error.message || 'Ping failed.'));
    }
  }

  async getAccessStatus() {
    if (process.platform !== 'linux') {
      try {
        await this.getStatus();
        return { supported: false, tokenReadable: null, serviceAvailable: true, error: null };
      } catch (error) {
        return { supported: false, tokenReadable: null, serviceAvailable: false, error: error.message };
      }
    }

    let tokenReadable = false;
    try {
      await fs.access(LINUX_TOKEN_PATH, fsConstants.R_OK);
      tokenReadable = true;
    } catch { /* Reported below. */ }

    try {
      await this.getStatus();
      return { supported: true, tokenReadable, serviceAvailable: true, error: null };
    } catch (error) {
      return { supported: true, tokenReadable, serviceAvailable: false, error: error.message };
    }
  }

  async repairAccess() {
    if (process.platform !== 'linux') throw new Error('Automatic access repair is available on Linux only.');
    const username = os.userInfo().username;
    if (!/^[a-z_][a-z0-9_.-]*[$]?$/i.test(username)) throw new Error('The current user name cannot be used for ACL repair.');

    try {
      await execFileAsync('/usr/bin/pkexec', [
        '/usr/bin/setfacl', '-m', `u:${username}:r`, LINUX_TOKEN_PATH,
      ], { encoding: 'utf8', timeout: 120_000, windowsHide: true, maxBuffer: 256 * 1024 });
    } catch (error) {
      if ([126, 127].includes(error.code)) throw new Error('Authorization was cancelled or denied.');
      const detail = String(error.stderr || error.stdout || error.message).trim();
      throw new Error(detail || 'Could not grant access to the ZeroTier service token.');
    }

    const status = await this.getAccessStatus();
    if (!status.tokenReadable) throw new Error('The token is still not readable after applying the ACL.');
    if (status.serviceAvailable) return status;

    try {
      await execFileAsync('/usr/bin/pkexec', [
        '/usr/bin/systemctl', 'start', 'zerotier-one.service',
      ], { encoding: 'utf8', timeout: 120_000, windowsHide: true, maxBuffer: 256 * 1024 });
    } catch (error) {
      if ([126, 127].includes(error.code)) throw new Error('Authorization was cancelled or denied.');
      const detail = String(error.stderr || error.stdout || error.message).trim();
      throw new Error(detail || 'Could not start the ZeroTier service.');
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
    const repaired = await this.getAccessStatus();
    if (!repaired.serviceAvailable) throw new Error(repaired.error || 'The ZeroTier service is still unavailable.');
    return repaired;
  }
}

module.exports = { ZeroTierCli, parsePingOutput };

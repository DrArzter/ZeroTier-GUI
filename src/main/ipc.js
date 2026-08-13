'use strict';

const { requireMemberId, requireNetworkId, requireToken } = require('../shared/validation');

function registerIpc({ ipcMain, shell, clipboard, providers, secrets, appearance }) {
  const { central, local } = providers;
  const handle = (channel, listener) => {
    ipcMain.handle(channel, async (_event, ...args) => listener(...args));
  };

  handle('settings:get-token-status', () => secrets.getStatus());
  handle('settings:set-token', async ({ token, persist }) => {
    const normalized = requireToken(token);
    try {
      await central.validateCredential(normalized);
    } catch (error) {
      throw new Error(`Token validation failed: ${error.message}`);
    }
    await secrets.setToken(normalized, Boolean(persist));
    return secrets.getStatus();
  });
  handle('settings:clear-token', async () => {
    await secrets.clear();
    return secrets.getStatus();
  });

  handle('central:get-status', () => central.getStatus());
  handle('central:get-networks', () => central.getNetworks());
  handle('central:get-network', (id) => central.getNetwork(requireNetworkId(id)));
  handle('central:get-members', (id) => central.getMembers(requireNetworkId(id)));
  handle('central:update-network', ({ networkId, data }) => {
    const config = data?.config || {};
    const name = String(config.name ?? '').trim().slice(0, 128);
    const description = String(config.description ?? '').trim().slice(0, 1024);
    const isPrivate = Boolean(config.private);
    return central.updateNetwork(requireNetworkId(networkId), { config: { name, description, private: isPrivate } });
  });
  handle('central:update-member', ({ networkId, memberId, data }) => {
    const name = String(data?.name ?? '').trim().slice(0, 128);
    const authorized = Boolean(data?.config?.authorized);
    return central.updateMember(requireNetworkId(networkId), requireMemberId(memberId), { name, config: { authorized } });
  });
  handle('central:create-network', () => central.createNetwork());
  handle('central:delete-network', (id) => central.deleteNetwork(requireNetworkId(id)));
  handle('central:delete-member', ({ networkId, memberId }) => (
    central.deleteMember(requireNetworkId(networkId), requireMemberId(memberId))
  ));

  handle('local:get-status', () => local.getStatus());
  handle('local:get-access-status', () => local.getAccessStatus());
  handle('local:repair-access', () => local.repairAccess());
  handle('local:get-networks', () => local.getNetworks());
  handle('local:join', (id) => local.join(requireNetworkId(id)));
  handle('local:leave', (id) => local.leave(requireNetworkId(id)));
  handle('local:set-network-setting', ({ networkId, setting, enabled }) => (
    local.setNetworkSetting(requireNetworkId(networkId), String(setting), Boolean(enabled))
  ));
  handle('local:ping', (address) => local.ping(String(address ?? '')));

  handle('app:open-external', async (url) => {
    const parsed = new URL(url);
    const allowed = new Set(['https://my.zerotier.com', 'https://www.zerotier.com', 'https://github.com']);
    if (!allowed.has(parsed.origin)) throw new Error('This external URL is not allowed.');
    await shell.openExternal(parsed.toString());
    return true;
  });
  handle('app:get-appearance', () => appearance.get());
  handle('app:copy-text', (value) => {
    const text = String(value ?? '').slice(0, 4096);
    if (!text) throw new Error('There is nothing to copy.');
    clipboard.writeText(text);
    return true;
  });
}

module.exports = { registerIpc };

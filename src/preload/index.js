'use strict';

const { contextBridge, ipcRenderer } = require('electron');

const invoke = (channel, payload) => ipcRenderer.invoke(channel, payload);

contextBridge.exposeInMainWorld('zerotier', Object.freeze({
  settings: Object.freeze({
    getTokenStatus: () => invoke('settings:get-token-status'),
    setToken: (payload) => invoke('settings:set-token', payload),
    clearToken: () => invoke('settings:clear-token'),
  }),
  central: Object.freeze({
    getStatus: () => invoke('central:get-status'),
    getNetworks: () => invoke('central:get-networks'),
    getNetwork: (id) => invoke('central:get-network', id),
    getMembers: (id) => invoke('central:get-members', id),
    updateNetwork: (networkId, data) => invoke('central:update-network', { networkId, data }),
    updateMember: (networkId, memberId, data) => invoke('central:update-member', { networkId, memberId, data }),
    createNetwork: () => invoke('central:create-network'),
    deleteNetwork: (id) => invoke('central:delete-network', id),
    deleteMember: (networkId, memberId) => invoke('central:delete-member', { networkId, memberId }),
  }),
  local: Object.freeze({
    getStatus: () => invoke('local:get-status'),
    getAccessStatus: () => invoke('local:get-access-status'),
    repairAccess: () => invoke('local:repair-access'),
    getNetworks: () => invoke('local:get-networks'),
    join: (id) => invoke('local:join', id),
    leave: (id) => invoke('local:leave', id),
    setNetworkSetting: (networkId, setting, enabled) => invoke('local:set-network-setting', { networkId, setting, enabled }),
    ping: (address) => invoke('local:ping', address),
  }),
  getAppearance: () => invoke('app:get-appearance'),
  copyText: (text) => invoke('app:copy-text', text),
  onAppearanceChanged: (callback) => {
    const listener = (_event, value) => callback(value);
    ipcRenderer.on('app:appearance-changed', listener);
    return () => ipcRenderer.removeListener('app:appearance-changed', listener);
  },
  openExternal: (url) => invoke('app:open-external', url),
}));

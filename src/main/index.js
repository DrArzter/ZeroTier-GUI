'use strict';

const path = require('node:path');
const fs = require('node:fs/promises');
const { app, BrowserWindow, clipboard, ipcMain, nativeTheme, safeStorage, shell, systemPreferences } = require('electron');
const { registerIpc } = require('./ipc');
const { SecretStore } = require('./services/secret-store');
const { ZeroTierApi } = require('./services/zerotier-api');
const { ZeroTierCli } = require('./services/zerotier-cli');
const { SystemAppearance } = require('./services/system-appearance');
const { CentralV1Adapter } = require('./providers/central-v1-adapter');
const { LocalCliAdapter } = require('./providers/local-cli-adapter');
const { ProviderStrategy } = require('./providers/provider-strategy');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 780,
    minHeight: 560,
    show: false,
    backgroundColor: '#0b1020',
    title: 'ZeroTier GUI',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      spellcheck: false,
      backgroundThrottling: true,
    },
  });

  mainWindow.loadFile(path.join(__dirname, '../../dist/renderer/index.html'));
  mainWindow.once('ready-to-show', () => {
    if (!process.env.ZEROTIER_GUI_SCREENSHOT) mainWindow?.show();
  });
  if (process.env.ZEROTIER_GUI_SCREENSHOT) {
    mainWindow.webContents.once('did-finish-load', () => {
      setTimeout(async () => {
        const image = await mainWindow?.webContents.capturePage();
        if (image) await fs.writeFile(process.env.ZEROTIER_GUI_SCREENSHOT, image.toPNG());
        app.quit();
      }, 1_000);
    });
  }
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.on('closed', () => { mainWindow = null; });
}

app.whenReady().then(() => {
  nativeTheme.themeSource = 'system';
  const secrets = new SecretStore({ safeStorage, userDataPath: app.getPath('userData') });
  const legacyApi = new ZeroTierApi({ getToken: () => secrets.getToken() });
  const cliClient = new ZeroTierCli();
  const providerStrategy = new ProviderStrategy({
    central: { 'legacy-v1': () => new CentralV1Adapter({ client: legacyApi }) },
    local: { 'zerotier-cli': () => new LocalCliAdapter({ client: cliClient }) },
  });
  const providers = providerStrategy.select();
  const appearance = new SystemAppearance({ nativeTheme, systemPreferences });
  registerIpc({ ipcMain, shell, clipboard, providers, secrets, appearance });
  createWindow();

  const broadcastAppearance = async (_event, accentColor = null) => {
    const value = await appearance.get();
    if (accentColor && value.platformStyle !== 'kde') {
      value.accentColor = `#${String(accentColor).replace(/^#/, '').slice(0, 6)}`;
      value.accentSource = 'system-event';
    }
    for (const window of BrowserWindow.getAllWindows()) window.webContents.send('app:appearance-changed', value);
  };
  nativeTheme.on('updated', broadcastAppearance);
  systemPreferences.on('accent-color-changed', broadcastAppearance);
  appearance.watch(broadcastAppearance);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Layout } from './components/Layout';
import { Modal } from './components/Modal';
import { ToastRegion } from './components/ToastRegion';
import { NetworksScreen } from './screens/NetworksScreen';
import { DetailsScreen } from './screens/DetailsScreen';
import { SettingsScreen } from './screens/SettingsScreen';
import { AboutScreen } from './screens/AboutScreen';

const bridge = window.zerotier;

function applyAppearance(value) {
  if (!value) return;
  const root = document.documentElement;
  root.dataset.platform = value.platformStyle;
  root.dataset.highContrast = String(value.highContrast);
  root.dataset.reducedMotion = String(value.reducedMotion);
  root.dataset.reducedTransparency = String(value.reducedTransparency);
  if (value.accentColor) root.style.setProperty('--system-accent', value.accentColor);
  else root.style.removeProperty('--system-accent');
  const paletteMap = {
    windowBackground: '--system-window-bg', windowAlternate: '--system-window-alt',
    windowText: '--system-window-text', inactiveText: '--system-inactive-text',
    viewBackground: '--system-view-bg', viewAlternate: '--system-view-alt',
    buttonBackground: '--system-button-bg', buttonText: '--system-button-text',
    negativeText: '--system-negative', positiveText: '--system-positive',
    selectionBackground: '--system-selection-bg', selectionText: '--system-selection-text',
  };
  for (const [name, cssVariable] of Object.entries(paletteMap)) {
    if (value.palette?.[name]) root.style.setProperty(cssVariable, value.palette[name]);
    else root.style.removeProperty(cssVariable);
  }
}

export function App() {
  const [route, setRoute] = useState({ name: 'settings' });
  const [header, setHeader] = useState({ title: 'ZeroTier', subtitle: 'Starting…' });
  const [localStatus, setLocalStatus] = useState(null);
  const [localNetworks, setLocalNetworks] = useState([]);
  const [appearance, setAppearance] = useState(null);
  const [modal, setModal] = useState(null);
  const [toasts, setToasts] = useState([]);
  const serviceWarningShown = useRef(false);

  const notify = useCallback((message, kind = '', options = {}) => {
    const id = crypto.randomUUID();
    setToasts((items) => [...items, { id, message, kind, action: options.action }]);
    setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), options.duration || 7000);
  }, []);

  const refreshLocal = useCallback(async () => {
    const [status, networks] = await Promise.allSettled([bridge.local.getStatus(), bridge.local.getNetworks()]);
    const nextStatus = status.status === 'fulfilled' ? status.value : null;
    setLocalStatus(nextStatus);
    setLocalNetworks(networks.status === 'fulfilled' && Array.isArray(networks.value) ? networks.value : []);
    if (!nextStatus && !serviceWarningShown.current) {
      serviceWarningShown.current = true;
      notify('Local ZeroTier service is unavailable. Open Settings to diagnose or repair access.', 'error', {
        action: { label: 'Open Settings', onClick: () => setRoute({ name: 'settings' }) },
        duration: 12_000,
      });
    }
    if (nextStatus) serviceWarningShown.current = false;
    return nextStatus;
  }, [notify]);

  useEffect(() => {
    document.documentElement.dataset.theme = 'system';
    localStorage.removeItem('theme');
    bridge.getAppearance().then((value) => { applyAppearance(value); setAppearance(value); });
    const unsubscribe = bridge.onAppearanceChanged((value) => { applyAppearance(value); setAppearance(value); });
    Promise.all([refreshLocal(), bridge.settings.getTokenStatus()]).then(([, token]) => {
      setRoute({ name: token.configured ? 'networks' : 'settings' });
    });
    return unsubscribe;
  }, [refreshLocal]);

  const navigate = useCallback((name, networkId) => setRoute({ name, networkId }), []);
  const context = useMemo(() => ({ bridge, navigate, notify, openModal: setModal, appearance, localStatus, localNetworks, refreshLocal, setHeader }), [navigate, notify, appearance, localStatus, localNetworks, refreshLocal]);
  let screen;
  if (route.name === 'networks') screen = <NetworksScreen {...context} />;
  if (route.name === 'details') screen = <DetailsScreen {...context} networkId={route.networkId} />;
  if (route.name === 'settings') screen = <SettingsScreen {...context} />;
  if (route.name === 'about') screen = <AboutScreen {...context} />;

  return <>
    <Layout route={route.name} navigate={navigate} localStatus={localStatus} header={header}>{screen}</Layout>
    <Modal model={modal} onClose={() => setModal(null)} notify={notify}/>
    <ToastRegion items={toasts}/>
  </>;
}

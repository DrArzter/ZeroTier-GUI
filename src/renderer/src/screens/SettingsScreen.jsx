import React, { useCallback, useEffect, useState } from 'react';
import { Button } from '../components/Button';
import { ErrorState, Loading } from '../components/Feedback';
import { errorMessage } from '../lib/errors';

export function SettingsScreen({ bridge, notify, refreshLocal, refreshCentralStatus, appearance, setHeader }) {
  const [status, setStatus] = useState(null);
  const [accessStatus, setAccessStatus] = useState(null);
  const [error, setError] = useState(null);
  const [token, setToken] = useState('');
  const [persist, setPersist] = useState(false);
  const [saving, setSaving] = useState(false);
  const [repairing, setRepairing] = useState(false);
  const load = useCallback(async () => {
    try {
      const [result, localAccess] = await Promise.all([bridge.settings.getTokenStatus(), bridge.local.getAccessStatus()]);
      setStatus(result); setAccessStatus(localAccess); setPersist(result.canPersist); setError(null);
    }
    catch (reason) { setError(errorMessage(reason)); }
  }, [bridge]);
  useEffect(() => { setHeader({ eyebrow: 'PREFERENCES', title: 'Settings', subtitle: 'Appearance, account access, and local integration.', actions: null }); }, [setHeader]);
  useEffect(() => { load(); }, [load]);

  const save = async () => {
    setSaving(true);
    try { await bridge.settings.setToken({ token, persist }); setToken(''); await refreshCentralStatus(); notify('Central mode enabled. Token validated and saved.', 'success'); await load(); }
    catch (reason) { notify(errorMessage(reason), 'error'); }
    finally { setSaving(false); }
  };
  const clear = async () => { await bridge.settings.clearToken(); await refreshCentralStatus(); notify('Token removed. Client-only mode is active.', 'success'); await load(); };
  const repairService = async () => {
    setRepairing(true);
    try {
      const repaired = await bridge.local.repairAccess();
      setAccessStatus(repaired);
      await refreshLocal();
      notify('Local ZeroTier integration repaired. The service is available.', 'success');
    } catch (reason) { notify(errorMessage(reason), 'error', { duration: 10_000 }); }
    finally { setRepairing(false); }
  };
  if (!status && !error) return <Loading/>;
  if (error) return <ErrorState error={error} retry={load}/>;

  return <>
    <section className="form-card">
      <h2>System appearance</h2><p>ZeroTier GUI follows the operating-system palette automatically.</p>
      <div className="security-note neutral appearance-summary"><span className="accent-swatch" style={{ background: appearance?.accentColor || 'var(--accent)' }}/><span>Detected: {appearance?.platformStyle || 'system'} · accent {appearance?.accentColor || 'automatic'} from {appearance?.accentSource || 'system'} · {appearance?.palette ? 'native KDE palette' : 'adaptive palette'}. System mode also follows contrast, motion, and transparency preferences.</span></div>
    </section>
    <section className="form-card">
      <h2>ZeroTier Central · optional</h2><p>{status.configured ? 'Central mode is enabled. You can manage hosted networks and their members.' : 'Client-only mode is active. Local networks, join, leave, ping, and client preferences work without a token.'} A new token is validated before it replaces the current one.</p>
      <div className="field"><label htmlFor="token">API token</label><input id="token" className="input" type="password" value={token} onChange={(event) => setToken(event.target.value)} placeholder={status.configured ? 'Token is configured' : 'Paste a new ZeroTier API token'} autoComplete="off" spellCheck="false"/></div>
      <label className="checkbox"><input type="checkbox" checked={persist} disabled={!status.canPersist} onChange={(event) => setPersist(event.target.checked)}/>Keep the token securely between app launches</label>
      <div className="security-note">{status.canPersist ? `Encrypted storage backend: ${status.backend}.` : 'A secure OS keyring is unavailable. The token will remain in memory only.'}</div>
      <div className="form-actions"><Button variant="primary" disabled={!token || saving} onClick={save}>Save and validate</Button><Button variant="danger" disabled={!status.configured} onClick={clear}>Remove token</Button></div>
    </section>
    <section className="form-card">
      <h2>Local ZeroTier service</h2><p>Joining, leaving, and pinging devices use zerotier-cli directly. The app never executes commands through a shell.</p>
      <div className={`service-diagnostic ${accessStatus?.serviceAvailable ? 'is-ok' : 'is-error'}`}>
        <span className="status-dot"></span>
        <div><strong>{accessStatus?.serviceAvailable ? 'Service available' : 'Service unavailable'}</strong><span>{accessStatus?.serviceAvailable ? 'The app can control the local ZeroTier node without root.' : accessStatus?.tokenReadable === false ? 'The current user cannot read the ZeroTier service token.' : accessStatus?.error || 'The local ZeroTier service could not be reached.'}</span></div>
      </div>
      <div className="form-actions">
        {!accessStatus?.serviceAvailable && accessStatus?.supported && <Button variant="primary" disabled={repairing} onClick={repairService}>{repairing ? 'Repairing…' : 'Fix local access'}</Button>}
        <Button onClick={async () => { const service = await refreshLocal(); const latest = await bridge.local.getAccessStatus(); setAccessStatus(latest); notify(service ? 'Local ZeroTier service is available.' : 'Service is still unavailable. Use Fix local access in Settings.', service ? 'success' : 'error'); }}>Check service now</Button>
      </div>
      {!accessStatus?.serviceAvailable && accessStatus?.supported && <div className="security-note">Fix local access opens one system authorization prompt. It grants the signed-in user read access only to ZeroTier's local service token and starts the service if necessary; the Electron app itself never runs as root.</div>}
    </section>
  </>;
}

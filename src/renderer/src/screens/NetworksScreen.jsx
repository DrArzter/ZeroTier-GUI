import React, { useCallback, useEffect, useState } from 'react';
import { Button } from '../components/Button';
import { Icon } from '../components/Icon';
import { EmptyState, ErrorState, Loading } from '../components/Feedback';
import { errorMessage } from '../lib/errors';
import { classifyLocalNetworks } from '../lib/network-memberships';

function NetworkCard({ network, local, onOpen }) {
  const config = network.config || {};
  const connected = String(local?.status || '').toUpperCase() === 'OK';
  return <article className="network-card" tabIndex="0" role="button" onClick={onOpen} onKeyDown={(event) => ['Enter', ' '].includes(event.key) && onOpen()}>
    <div className="network-card-top">
      <div><h2>{config.name || network.name || 'Unnamed network'}</h2><div className="network-id">{network.id}</div></div>
      {local ? <span className={`pill ${connected ? 'online' : 'pending'}`}>{connected ? 'Connected' : local.status || 'Joined'}</span> : <span className={`pill ${config.private ? 'private' : ''}`}>{config.private ? 'Private' : 'Public'}</span>}
    </div>
    <div className="network-card-bottom">
      <div className="network-counts">
        <div><strong>{network.onlineMemberCount ?? '—'}</strong><span>online</span></div>
        <div><strong>{network.authorizedMemberCount ?? '—'}</strong><span>authorized</span></div>
        <div><strong>{network.totalMemberCount ?? '—'}</strong><span>members</span></div>
      </div>
      <span className="arrow-chip"><Icon name="arrow"/></span>
    </div>
  </article>;
}

export function NetworksScreen({ bridge, navigate, notify, openModal, localNetworks, refreshLocal, setHeader }) {
  const [networks, setNetworks] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setNetworks(null); setError(null);
    try {
      const [items] = await Promise.all([bridge.central.getNetworks(), refreshLocal()]);
      setNetworks(Array.isArray(items) ? items : []);
    } catch (reason) { setError(errorMessage(reason)); }
  }, [bridge, refreshLocal]);

  const join = useCallback(() => {
    let value = '';
    openModal({
      title: 'Join a network', description: 'Enter the 16-character network ID. This affects the local ZeroTier node.', confirmLabel: 'Join network',
      content: <div className="field"><label>Network ID</label><input className="input" maxLength="16" autoComplete="off" placeholder="8056c2e21c000001" onChange={(event) => { value = event.target.value; }}/></div>,
      onConfirm: async () => { await bridge.local.join(value); await refreshLocal(); notify('The local node joined the network.', 'success'); },
    });
  }, [bridge, notify, openModal, refreshLocal]);

  const create = useCallback(() => openModal({
    title: 'Create a network', description: 'ZeroTier Central will create a private network with default settings.', confirmLabel: 'Create network',
    content: <div className="security-note">Creating a network changes your ZeroTier account and may count toward account limits.</div>,
    onConfirm: async () => { const network = await bridge.central.createNetwork(); notify('Network created.', 'success'); if (network?.id) navigate('details', network.id); else load(); },
  }), [bridge, load, navigate, notify, openModal]);

  useEffect(() => { setHeader({ title: 'Networks', subtitle: 'Manage your virtual networks and connected devices.', actions: <><Button className="icon-button" icon="refresh" title="Refresh" onClick={load}/><Button onClick={join}>Join</Button><Button variant="primary" icon="plus" onClick={create}>Create network</Button></> }); }, [create, join, load, setHeader]);
  useEffect(() => { load(); }, [load]);

  if (!networks && !error) return <Loading/>;
  if (error?.includes('token is not configured')) return <EmptyState title="API token required" description="Add a ZeroTier Central API token in Settings. It is sent only to the official ZeroTier API." action={<Button variant="primary" onClick={() => navigate('settings')}>Open settings</Button>}/>;
  if (error) return <ErrorState error={error} retry={load}/>;
  if (!networks.length) return <EmptyState title="No networks yet" description="Create a network in ZeroTier Central, or join an existing network on this device." action={<Button variant="primary" icon="plus" onClick={create}>Create your first network</Button>}/>;

  const online = networks.reduce((sum, network) => sum + Number(network.onlineMemberCount || 0), 0);
  const { connected: connectedLocally, stale: staleLocalNetworks } = classifyLocalNetworks(networks, localNetworks);
  const leaveStale = (network) => {
    const id = String(network.nwid || network.id);
    openModal({
      title: 'Remove stale local membership?',
      description: `${network.name || id} no longer exists in ZeroTier Central. Leaving removes only its stale membership from this device.`,
      confirmLabel: 'Leave locally',
      danger: true,
      onConfirm: async () => {
        await bridge.local.leave(id);
        await refreshLocal();
        notify('Stale local membership removed.', 'success');
      },
    });
  };
  return <>
    <div className="stats-row">
      <div className="stat-card"><span>Central networks</span><strong>{networks.length}</strong></div>
      <div className="stat-card"><span>Members online</span><strong>{online}</strong></div>
      <div className="stat-card"><span>Connected locally</span><strong>{connectedLocally.length}</strong></div>
    </div>
    {staleLocalNetworks.length > 0 && <section className="stale-panel">
      <div className="stale-panel-copy">
        <strong>{staleLocalNetworks.length} stale local {staleLocalNetworks.length === 1 ? 'membership' : 'memberships'}</strong>
        <span>These networks were removed from Central but are still stored on this device.</span>
      </div>
      <div className="stale-network-list">
        {staleLocalNetworks.map((network) => {
          const id = String(network.nwid || network.id);
          return <div className="stale-network" key={id}><div><strong>{network.name || 'Deleted network'}</strong><span>{id}</span></div><Button variant="danger" onClick={() => leaveStale(network)}>Leave</Button></div>;
        })}
      </div>
    </section>}
    <div className="network-grid">{networks.map((network) => <NetworkCard key={network.id} network={network} local={localNetworks.find((item) => String(item.nwid || item.id) === network.id)} onOpen={() => navigate('details', network.id)}/>)}</div>
  </>;
}

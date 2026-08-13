import React, { useCallback, useEffect, useState } from 'react';
import { Button } from '../components/Button';
import { Icon } from '../components/Icon';
import { PingResult } from '../components/PingResult';
import { EmptyState, ErrorState, Loading } from '../components/Feedback';
import { errorMessage } from '../lib/errors';
import { classifyLocalNetworks } from '../lib/network-memberships';

const localSettings = [
  ['allowManaged', 'Managed addresses and routes'],
  ['allowDNS', 'ZeroTier DNS'],
  ['allowGlobal', 'Global routes'],
  ['allowDefault', 'Default route'],
];

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

function LocalNetworkCard({ network, bridge, notify, openModal, reload }) {
  const id = String(network.nwid || network.id);
  const addresses = Array.isArray(network.assignedAddresses) ? network.assignedAddresses : [];
  const connected = String(network.status || '').toUpperCase() === 'OK';
  const copyAddress = async (address) => {
    try { await bridge.copyText(address); notify(`Copied ${address}`, 'success'); }
    catch (reason) { notify(errorMessage(reason), 'error'); }
  };
  const ping = () => {
    let address = '';
    openModal({
      title: 'Ping a ZeroTier address',
      description: `Test reachability through ${network.name || id}. Enter another member's managed IP address.`,
      confirmLabel: 'Ping',
      content: <div className="field"><label>Target IP address</label><input className="input" autoComplete="off" placeholder="10.147.17.101" onChange={(event) => { address = event.target.value.trim(); }}/></div>,
      onConfirm: async () => {
        const result = await bridge.local.ping(address);
        openModal({
          title: `Connection test · ${address}`,
          description: result.success ? 'The device replied over ZeroTier.' : 'The device did not reply. It may be offline or blocking ICMP.',
          confirmLabel: 'Close', hideCancel: true, onConfirm: async () => {},
          content: <PingResult result={result} address={address} copyAddress={() => copyAddress(address)}/>,
        });
        return { close: false };
      },
    });
  };
  const preferences = () => {
    const next = Object.fromEntries(localSettings.map(([setting]) => [setting, Boolean(network[setting])]));
    openModal({
      title: 'Local network preferences',
      description: `These settings affect only this device on ${network.name || id}.`,
      confirmLabel: 'Apply',
      content: <div className="modal-form local-preferences-modal">{localSettings.map(([setting, label]) => <label className="checkbox" key={setting}><input type="checkbox" defaultChecked={next[setting]} onChange={(event) => { next[setting] = event.target.checked; }}/>{label}</label>)}</div>,
      onConfirm: async () => {
        await Promise.all(localSettings.map(([setting]) => bridge.local.setNetworkSetting(id, setting, next[setting])));
        await reload();
        notify('Local network preferences updated.', 'success');
      },
    });
  };
  const leave = () => openModal({
    title: 'Leave this network?', description: `${network.name || id} will be removed only from this device.`, confirmLabel: 'Leave locally', danger: true,
    onConfirm: async () => { await bridge.local.leave(id); await reload(); notify('Local node left the network.', 'success'); },
  });

  return <article className="network-card local-network-card">
    <div className="network-card-top"><div><h2>{network.name || 'Unnamed network'}</h2><div className="network-id">{id}</div></div><span className={`pill ${connected ? 'online' : 'pending'}`}>{connected ? 'Connected' : network.status || 'Joined'}</span></div>
    <div className="local-address-list">{addresses.length ? addresses.map((address) => <div key={address}><span>{address}</span><button type="button" onClick={() => copyAddress(address)}>Copy</button></div>) : <span>No managed IP assigned</span>}</div>
    <div className="local-card-actions"><Button onClick={ping}>Ping address</Button><Button onClick={preferences}>Preferences</Button><Button variant="danger" onClick={leave}>Leave</Button></div>
  </article>;
}

export function NetworksScreen({ bridge, centralConfigured, navigate, notify, openModal, localNetworks, refreshLocal, setHeader }) {
  const [networks, setNetworks] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setNetworks(null); setError(null);
    try {
      if (!centralConfigured) {
        await refreshLocal();
        setNetworks([]);
        return;
      }
      const [items] = await Promise.all([bridge.central.getNetworks(), refreshLocal()]);
      setNetworks(Array.isArray(items) ? items : []);
    } catch (reason) { setError(errorMessage(reason)); }
  }, [bridge, centralConfigured, refreshLocal]);

  const join = useCallback(() => {
    let value = '';
    openModal({
      title: 'Join a network', description: 'Enter the 16-character network ID. This affects the local ZeroTier node.', confirmLabel: 'Join network',
      content: <div className="field"><label>Network ID</label><input className="input" maxLength="16" autoComplete="off" placeholder="8056c2e21c000001" onChange={(event) => { value = event.target.value; }}/></div>,
      onConfirm: async () => { await bridge.local.join(value); await load(); notify('The local node joined the network.', 'success'); },
    });
  }, [bridge, load, notify, openModal]);

  const create = useCallback(() => openModal({
    title: 'Create a network', description: 'ZeroTier Central will create a private network with default settings.', confirmLabel: 'Create network',
    content: <div className="security-note">Creating a network changes your ZeroTier account and may count toward account limits.</div>,
    onConfirm: async () => { const network = await bridge.central.createNetwork(); notify('Network created.', 'success'); if (network?.id) navigate('details', network.id); else load(); },
  }), [bridge, load, navigate, notify, openModal]);

  useEffect(() => { setHeader({ eyebrow: centralConfigured ? 'CENTRAL + CLIENT' : 'CLIENT ONLY', title: 'Networks', subtitle: centralConfigured ? 'Manage Central networks and this device.' : 'Manage networks joined on this device without a Central token.', actions: <><Button className="icon-button" icon="refresh" title="Refresh" onClick={load}/><Button onClick={join}>Join</Button>{centralConfigured && <Button variant="primary" icon="plus" onClick={create}>Create network</Button>}</> }); }, [centralConfigured, create, join, load, setHeader]);
  useEffect(() => { load(); }, [load]);

  if (!networks && !error) return <Loading/>;
  if (error) return <ErrorState error={error} retry={load}/>;

  if (!centralConfigured) return <>
    <div className="stats-row client-stats"><div className="stat-card"><span>Mode</span><strong>Client only</strong></div><div className="stat-card"><span>Joined locally</span><strong>{localNetworks.length}</strong></div><div className="stat-card"><span>Connected</span><strong>{localNetworks.filter((network) => String(network.status || '').toUpperCase() === 'OK').length}</strong></div></div>
    {localNetworks.length ? <div className="network-grid">{localNetworks.map((network) => <LocalNetworkCard key={network.nwid || network.id} network={network} bridge={bridge} notify={notify} openModal={openModal} reload={load}/>)}</div> : <EmptyState title="No local networks" description="Join a network by ID. A Central token is optional for local client management." action={<Button variant="primary" onClick={join}>Join a network</Button>}/>}</>;

  if (!networks.length) return <EmptyState title="No Central networks yet" description="Create a network in ZeroTier Central, or join an existing network on this device." action={<Button variant="primary" icon="plus" onClick={create}>Create your first network</Button>}/>;

  const online = networks.reduce((sum, network) => sum + Number(network.onlineMemberCount || 0), 0);
  const { connected: connectedLocally, stale: staleLocalNetworks } = classifyLocalNetworks(networks, localNetworks);
  const leaveStale = (network) => {
    const id = String(network.nwid || network.id);
    openModal({
      title: 'Remove stale local membership?', description: `${network.name || id} no longer exists in ZeroTier Central. Leaving removes only its stale membership from this device.`, confirmLabel: 'Leave locally', danger: true,
      onConfirm: async () => { await bridge.local.leave(id); await load(); notify('Stale local membership removed.', 'success'); },
    });
  };
  return <>
    <div className="stats-row"><div className="stat-card"><span>Central networks</span><strong>{networks.length}</strong></div><div className="stat-card"><span>Members online</span><strong>{online}</strong></div><div className="stat-card"><span>Connected locally</span><strong>{connectedLocally.length}</strong></div></div>
    {staleLocalNetworks.length > 0 && <section className="stale-panel"><div className="stale-panel-copy"><strong>{staleLocalNetworks.length} stale local {staleLocalNetworks.length === 1 ? 'membership' : 'memberships'}</strong><span>These networks were removed from Central but are still stored on this device.</span></div><div className="stale-network-list">{staleLocalNetworks.map((network) => { const id = String(network.nwid || network.id); return <div className="stale-network" key={id}><div><strong>{network.name || 'Deleted network'}</strong><span>{id}</span></div><Button variant="danger" onClick={() => leaveStale(network)}>Leave</Button></div>; })}</div></section>}
    <div className="network-grid">{networks.map((network) => <NetworkCard key={network.id} network={network} local={localNetworks.find((item) => String(item.nwid || item.id) === network.id)} onOpen={() => navigate('details', network.id)}/>)}</div>
  </>;
}

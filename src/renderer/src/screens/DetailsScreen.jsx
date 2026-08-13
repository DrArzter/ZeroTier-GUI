import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button } from '../components/Button';
import { Icon } from '../components/Icon';
import { PingResult } from '../components/PingResult';
import { EmptyState, ErrorState, Loading } from '../components/Feedback';
import { errorMessage } from '../lib/errors';

const formatDate = (timestamp) => timestamp ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(timestamp)) : 'Not available';
const formatLastSeen = (timestamp) => {
  if (!timestamp) return 'Never seen';
  const elapsedSeconds = Math.max(0, Math.round((Date.now() - timestamp) / 1000));
  if (elapsedSeconds < 60) return 'Just now';
  if (elapsedSeconds < 3600) return `${Math.floor(elapsedSeconds / 60)} min ago`;
  if (elapsedSeconds < 86400) return `${Math.floor(elapsedSeconds / 3600)} h ago`;
  return `${Math.floor(elapsedSeconds / 86400)} d ago`;
};
const InfoCell = ({ label, children }) => <div className="info-cell"><span>{label}</span><strong>{children ?? 'Not available'}</strong></div>;

function MemberRow({ member, networkId, localStatus, bridge, notify, openModal, reload }) {
  const config = member.config || {};
  const id = member.nodeId || config.address || member.id || '';
  const addresses = config.ipAssignments || member.ipAssignments || [];
  const address = addresses[0];
  const copyAddress = async () => {
    try { await bridge.copyText(address); notify(`Copied ${address}`, 'success'); }
    catch (error) { notify(errorMessage(error), 'error'); }
  };
  const ping = async () => {
    try {
      const result = await bridge.local.ping(address);
      openModal({
        title: `Connection test · ${member.name || id}`,
        description: result.success ? 'The device replied over its ZeroTier address.' : 'The device did not reply. It may be offline or blocking ICMP.',
        confirmLabel: 'Close', hideCancel: true, onConfirm: async () => {},
        content: <PingResult result={result} address={address} copyAddress={copyAddress}/>,
      });
    }
    catch (error) { notify(errorMessage(error), 'error'); }
  };
  const remove = () => openModal({
    title: 'Remove network member?', description: `${member.name || id} will be removed from this network in ZeroTier Central.`, confirmLabel: 'Remove member', danger: true,
    onConfirm: async () => { await bridge.central.deleteMember(networkId, id); notify('Member removed.', 'success'); reload(); },
  });
  const manage = () => {
    let nextName = member.name || '';
    let authorized = Boolean(config.authorized);
    openModal({
      title: 'Manage network member', description: `Update ${member.name || id} in ZeroTier Central.`, confirmLabel: 'Save member',
      content: <div className="modal-form"><div className="field"><label>Member name</label><input className="input" defaultValue={nextName} maxLength="128" onChange={(event) => { nextName = event.target.value; }}/></div><label className="checkbox"><input type="checkbox" defaultChecked={authorized} onChange={(event) => { authorized = event.target.checked; }}/>Authorized to access this network</label></div>,
      onConfirm: async () => { await bridge.central.updateMember(networkId, id, { name: nextName, config: { authorized } }); notify('Member updated.', 'success'); reload(); },
    });
  };
  return <div className="member-row">
    <div className="member-name"><strong>{member.name || 'Unnamed member'}{localStatus?.address === id ? ' · You' : ''}</strong><span>{id}</span><small title={member.lastSeen ? formatDate(member.lastSeen) : undefined}>Last seen {formatLastSeen(member.lastSeen)}</small></div>
    <div className="member-address-cell"><span className="member-address">{address || 'No assigned IP'}</span>{address && <button className="copy-address" type="button" onClick={copyAddress}>Copy IP</button>}</div>
    <span className={`pill ${member.online ? 'online' : ''}`}>{member.online ? 'Online' : config.authorized ? 'Authorized' : 'Pending'}</span>
    <div className="member-actions">{addresses[0] && <Button onClick={ping}>Ping</Button>}<Button onClick={manage}>Manage</Button><Button variant="danger" onClick={remove}>Remove</Button></div>
  </div>;
}

export function DetailsScreen({ networkId, bridge, navigate, notify, openModal, localStatus, localNetworks, refreshLocal, setHeader }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState('');
  const [localUpdating, setLocalUpdating] = useState(null);
  const load = useCallback(async () => {
    setData(null); setError(null);
    try { const [network, members, account] = await Promise.all([bridge.central.getNetwork(networkId), bridge.central.getMembers(networkId), bridge.central.getStatus(), refreshLocal()]); setData({ network, members: Array.isArray(members) ? members : [], account }); }
    catch (reason) { setError(errorMessage(reason)); }
  }, [bridge, networkId, refreshLocal]);
  useEffect(() => { load(); }, [load]);
  useEffect(() => { setHeader({ eyebrow: 'NETWORK DETAILS', title: data?.network?.config?.name || (data ? 'Unnamed network' : 'Loading network…'), subtitle: networkId, actions: <><Button icon="back" onClick={() => navigate('networks')}>Back</Button><Button className="icon-button" icon="refresh" title="Refresh" onClick={load}/></> }); }, [data, load, navigate, networkId, setHeader]);

  const filtered = useMemo(() => (data?.members || []).filter((member) => {
    const config = member.config || {}; return `${member.name || ''} ${member.nodeId || config.address || ''} ${(config.ipAssignments || []).join(' ')}`.toLowerCase().includes(query.toLowerCase());
  }), [data, query]);
  if (!data && !error) return <Loading/>;
  if (error) return <ErrorState error={error} retry={load}/>;

  const { network, members, account } = data;
  const config = network.config || {};
  const userId = account?.user?.id;
  const ownNetwork = Boolean(userId && network.ownerId === userId);
  const userPermissions = userId ? network.permissions?.[userId] : null;
  const accessLevel = ownNetwork ? 'Owner' : userPermissions && (userPermissions.m || userPermissions.a || userPermissions.d) ? 'Shared admin' : 'Shared access';
  const name = config.name || 'Unnamed network';
  const local = localNetworks.find((item) => String(item.nwid || item.id) === networkId);
  const connected = String(local?.status || '').toUpperCase() === 'OK';
  const toggleLocal = async () => { try { if (local) await bridge.local.leave(networkId); else await bridge.local.join(networkId); await refreshLocal(); notify(local ? 'Local node left the network.' : 'Local node joined the network.', 'success'); } catch (reason) { notify(errorMessage(reason), 'error'); } };
  const removeNetwork = () => openModal({ title: 'Delete this network?', description: `${name} and its Central configuration will be permanently deleted.`, confirmLabel: 'Delete network', danger: true, onConfirm: async () => { await bridge.central.deleteNetwork(networkId); notify('Network deleted.', 'success'); navigate('networks'); } });
  const editNetwork = () => {
    let nextName = config.name || '';
    let description = config.description || '';
    let isPrivate = Boolean(config.private);
    openModal({
      title: 'Edit network', description: 'Update the basic ZeroTier Central configuration.', confirmLabel: 'Save network',
      content: <div className="modal-form"><div className="field"><label>Network name</label><input className="input" defaultValue={nextName} maxLength="128" onChange={(event) => { nextName = event.target.value; }}/></div><div className="field"><label>Description</label><textarea className="input textarea" defaultValue={description} maxLength="1024" onChange={(event) => { description = event.target.value; }}/></div><label className="checkbox"><input type="checkbox" defaultChecked={isPrivate} onChange={(event) => { isPrivate = event.target.checked; }}/>Private network — members require authorization</label></div>,
      onConfirm: async () => { await bridge.central.updateNetwork(networkId, { config: { name: nextName, description, private: isPrivate } }); notify('Network updated.', 'success'); load(); },
    });
  };
  const updateLocalSetting = async (setting, enabled) => {
    setLocalUpdating(setting);
    try { await bridge.local.setNetworkSetting(networkId, setting, enabled); await refreshLocal(); notify('Local network preference updated.', 'success'); }
    catch (reason) { notify(errorMessage(reason), 'error'); }
    finally { setLocalUpdating(null); }
  };

  return <>
    <section className="detail-hero">
      <div><div className="hero-pills"><span className={`pill ${connected ? 'online' : local ? 'pending' : 'private'}`}>{connected ? 'Connected locally' : local ? local.status || 'Joined locally' : 'Not joined locally'}</span><span className={`pill ${ownNetwork ? 'private' : ''}`}>{accessLevel}</span></div><h2>{name}</h2><div className="network-id">{networkId}</div></div>
      <div className="detail-actions"><Button onClick={editNetwork}>Edit network</Button><Button icon="external" onClick={() => bridge.openExternal(`https://my.zerotier.com/network/${networkId}`)}>Open Central</Button><Button variant={local ? '' : 'primary'} onClick={toggleLocal}>{local ? 'Leave locally' : 'Join locally'}</Button><Button variant="danger" onClick={removeNetwork}>Delete</Button></div>
    </section>
    <section className="info-grid"><InfoCell label="Network access">{config.private ? 'Private' : 'Public'}</InfoCell><InfoCell label="Your role">{accessLevel}</InfoCell><InfoCell label="Members online">{network.onlineMemberCount ?? 0}</InfoCell><InfoCell label="Authorized members">{network.authorizedMemberCount ?? 0}</InfoCell><InfoCell label="MTU">{config.mtu || 'Default'}</InfoCell><InfoCell label="Created">{formatDate(config.creationTime)}</InfoCell></section>
    {local && <section className="panel local-settings-panel">
      <div className="panel-header"><div><h2>Local preferences</h2><p>These settings affect only this device and are applied through zerotier-cli.</p></div></div>
      <div className="local-setting-list">
        {[
          ['allowManaged', 'Managed addresses and routes', 'Allow ZeroTier to configure private IP addresses and managed routes.'],
          ['allowDNS', 'ZeroTier DNS', 'Allow this network to configure DNS servers on this device.'],
          ['allowGlobal', 'Global routes', 'Allow managed routes to public, non-private address ranges.'],
          ['allowDefault', 'Default route', 'Allow this network to replace the system default route.'],
        ].map(([setting, label, description]) => <label className="local-setting" key={setting}><div><strong>{label}</strong><span>{description}</span></div><input type="checkbox" checked={Boolean(local[setting])} disabled={Boolean(localUpdating)} onChange={(event) => updateLocalSetting(setting, event.target.checked)}/></label>)}
      </div>
    </section>}
    <section className="panel">
      <div className="panel-header"><div><h2>Members · {members.length}</h2><p>Devices known to ZeroTier Central for this network.</p></div><label className="search-box"><Icon name="search"/><input placeholder="Search members…" value={query} onChange={(event) => setQuery(event.target.value)}/></label></div>
      <div className="member-list">{filtered.length ? filtered.map((member) => <MemberRow key={member.nodeId || member.config?.address || member.id} member={member} networkId={networkId} localStatus={localStatus} bridge={bridge} notify={notify} openModal={openModal} reload={load}/>) : <EmptyState title={members.length ? 'No matching members' : 'No members yet'} description={members.length ? 'Try another search.' : 'Join a device to this network to see it here.'}/>}</div>
    </section>
  </>;
}

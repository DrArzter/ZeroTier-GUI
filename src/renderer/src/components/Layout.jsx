import React from 'react';
import { Icon } from './Icon';
import appIcon from '../assets/app-icon.png';

const navItems = [
  ['networks', 'grid', 'Networks'],
  ['settings', 'settings', 'Settings'],
  ['about', 'info', 'About'],
];

export function Layout({ route, navigate, localStatus, header, children }) {
  const activeRoute = route === 'details' ? 'networks' : route;
  const online = Boolean(localStatus);
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand" aria-label="ZeroTier GUI">
        <img className="brand-mark" src={appIcon} alt=""/>
        <div className="brand-copy"><strong>ZeroTier</strong></div>
      </div>
      <nav className="nav" aria-label="Main navigation">
        {navItems.map(([id, icon, label]) => <button className={`nav-item ${activeRoute === id ? 'is-active' : ''}`} onClick={() => navigate(id)} key={id}><Icon name={icon}/><span>{label}</span></button>)}
      </nav>
      <div className="sidebar-status">
        <span className={`status-dot ${online ? 'is-online' : 'is-error'}`}></span>
        <div><strong>{online ? (localStatus.online === false ? 'Service offline' : 'Service online') : 'Service unavailable'}</strong><span>{online ? (localStatus.address || localStatus.nodeId || 'Node connected') : 'Check zerotier-cli access'}</span></div>
      </div>
    </aside>
    <main className="main">
      <header className="topbar">
        <div><div className="eyebrow">{header.eyebrow || 'CENTRAL'}</div><h1>{header.title}</h1><p>{header.subtitle}</p></div>
        <div className="topbar-actions">{header.actions}</div>
      </header>
      <section className="content" aria-live="polite">{children}</section>
    </main>
  </div>;
}

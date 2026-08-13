import React, { useEffect } from 'react';
import { Button } from '../components/Button';

const features = [
  ['Central networks', 'View networks, members, status, and account-backed configuration.'],
  ['Local control', 'Join and leave networks through zerotier-cli without running the UI as root.'],
  ['Secure boundary', 'An isolated renderer receives only a small, validated IPC interface.'],
  ['Low overhead', 'No Redux, component framework, polling loop, or eager member requests.'],
];

export function AboutScreen({ bridge, setHeader }) {
  useEffect(() => { setHeader({ eyebrow: 'APPLICATION', title: 'About', subtitle: 'A focused ZeroTier desktop client.', actions: null }); }, [setHeader]);
  return <div className="about-layout">
    <h2>ZeroTier GUI</h2>
    <p>A compact desktop interface for ZeroTier Central and the local ZeroTier service. React keeps the UI modular; Electron account operations and local commands remain outside the renderer.</p>
    <div className="feature-list">{features.map(([title, text]) => <div className="feature" key={title}><strong>{title}</strong><span>{text}</span></div>)}</div>
    <div className="form-actions"><Button icon="external" onClick={() => bridge.openExternal('https://github.com/DrArzter/zerotier-gui')}>Project on GitHub</Button><Button icon="external" onClick={() => bridge.openExternal('https://www.zerotier.com')}>ZeroTier website</Button></div>
  </div>;
}

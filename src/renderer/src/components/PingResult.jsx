import React from 'react';
import { Button } from './Button';

const InfoCell = ({ label, children }) => <div className="info-cell"><span>{label}</span><strong>{children ?? '—'}</strong></div>;

export function PingResult({ result, address, copyAddress }) {
  return <div className="ping-result">
    <div className={`ping-summary ${result.success ? 'is-success' : 'is-error'}`}><span className="status-dot"/><div><strong>{result.success ? 'Reachable' : 'Unreachable'}</strong><span>{address}</span></div><Button onClick={copyAddress}>Copy IP</Button></div>
    <div className="ping-metrics"><InfoCell label="Latency">{result.latencyMs == null ? '—' : `${result.latencyMs.toFixed(1)} ms`}</InfoCell><InfoCell label="Packet loss">{result.packetLossPercent == null ? '—' : `${result.packetLossPercent}%`}</InfoCell><InfoCell label="Replies">{result.packetsReceived == null ? '—' : `${result.packetsReceived}/${result.packetsTransmitted}`}</InfoCell></div>
    {result.error && <div className="ping-error">{result.error}</div>}
    {result.raw && <details className="ping-raw"><summary>Technical output</summary><pre>{result.raw}</pre></details>}
  </div>;
}

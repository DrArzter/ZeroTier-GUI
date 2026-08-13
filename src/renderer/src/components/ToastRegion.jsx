import React from 'react';

export function ToastRegion({ items }) {
  return <div className="toast-region" aria-live="assertive">{items.map((item) => <div className={`toast ${item.kind}`} key={item.id}><span>{item.message}</span>{item.action && <button type="button" onClick={item.action.onClick}>{item.action.label}</button>}</div>)}</div>;
}

import React from 'react';
import { Button } from './Button';

export function Loading() {
  return <div className="skeleton-grid">{[0, 1, 2, 3].map((key) => <div className="skeleton" key={key} />)}</div>;
}

export function EmptyState({ title, description, action, mark = 'Z' }) {
  return <div className="empty-state"><div className="empty-icon">{mark}</div><h2>{title}</h2><p>{description}</p>{action}</div>;
}

export function ErrorState({ error, retry }) {
  return <div className="error-state"><div className="empty-icon">!</div><h2>Something went wrong</h2><p>{error}</p>{retry && <Button variant="primary" onClick={retry}>Try again</Button>}</div>;
}

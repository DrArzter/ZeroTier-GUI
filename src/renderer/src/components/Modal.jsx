import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Button } from './Button';
import { errorMessage } from '../lib/errors';

export function Modal({ model, onClose, notify }) {
  const [pending, setPending] = useState(false);
  useEffect(() => {
    setPending(false);
  }, [model]);
  useEffect(() => {
    const closeOnEscape = (event) => event.key === 'Escape' && onClose();
    document.addEventListener('keydown', closeOnEscape);
    return () => document.removeEventListener('keydown', closeOnEscape);
  }, [onClose]);

  if (!model) return null;
  const confirm = async () => {
    setPending(true);
    try {
      const result = await model.onConfirm?.();
      setPending(false);
      if (result?.close === false) return;
      onClose();
    }
    catch (error) { notify(errorMessage(error), 'error'); setPending(false); }
  };
  return createPortal(
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true">
        <h2>{model.title}</h2>{model.description && <p>{model.description}</p>}{model.content}
        <div className="modal-actions">
          {!model.hideCancel && <Button onClick={onClose}>{model.cancelLabel || 'Cancel'}</Button>}
          <Button variant={model.danger ? 'danger' : 'primary'} disabled={pending} onClick={confirm}>{model.confirmLabel || 'Confirm'}</Button>
        </div>
      </div>
    </div>, document.body,
  );
}

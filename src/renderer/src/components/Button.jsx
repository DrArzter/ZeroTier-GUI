import React from 'react';
import { Icon } from './Icon';

export function Button({ children, variant = '', icon, className = '', ...props }) {
  return (
    <button className={`button ${variant} ${className}`.trim()} type="button" {...props}>
      {icon && <Icon name={icon} />}
      {children}
    </button>
  );
}

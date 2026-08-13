export function errorMessage(error) {
  return String(error?.message || error || 'Unknown error')
    .replace(/^Error invoking remote method '[^']+': Error: /, '');
}

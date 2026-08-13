export function classifyLocalNetworks(centralNetworks, localNetworks) {
  const centralIds = new Set(centralNetworks.map((network) => String(network.id)));
  return {
    connected: localNetworks.filter((network) => (
      centralIds.has(String(network.nwid || network.id))
      && String(network.status || '').toUpperCase() === 'OK'
    )),
    stale: localNetworks.filter((network) => (
      !centralIds.has(String(network.nwid || network.id))
      && String(network.status || '').toUpperCase() === 'NOT_FOUND'
    )),
  };
}

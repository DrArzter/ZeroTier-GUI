# ZeroTier GUI

<p align="center"><img src="build/icon.png" width="128" alt="ZeroTier GUI icon"></p>

A lightweight desktop client for managing Legacy ZeroTier Central networks and the local ZeroTier service.

The current application is a complete Electron + React rewrite of the original Python/GTK client. It keeps privileged and network-facing operations in Electron's main process while the sandboxed renderer receives a small validated IPC API.

> [!NOTE]
> ZeroTier GUI currently supports the Legacy Central v1 API and local `zerotier-cli`. The provider boundary is ready for a future Central v2 adapter, but v2 credentials and organizations are not implemented yet.

## Features

- Create, edit, inspect, and delete Central networks
- Run in client-only mode without a Central token
- View, search, rename, authorize, ping, and remove network members
- Display member connectivity, assigned IP addresses, last-seen time, and network ownership/access level
- Copy member IP addresses directly from the member list or ping result
- Join and leave networks on the local device
- Ping arbitrary managed addresses and change local network preferences in client-only mode
- Configure managed addresses, DNS, global routes, and default-route preferences per network
- Detect stale local memberships for networks removed from Central and clean them up
- Diagnose Linux access to the ZeroTier service and repair it without running the application as root
- Follow the operating-system light/dark mode, contrast, motion, transparency, palette, and accent preferences
- Use the native KDE palette where available

## Requirements

- Node.js 22 or newer
- A Legacy ZeroTier Central personal API token
- ZeroTier One and `zerotier-cli` for local device management
- Linux access repair additionally requires `pkexec`, `setfacl`, and `systemctl`

## Running from source

```bash
npm install
npm start
```

Useful development commands:

```bash
npm run build
npm run check
npm test
```

The application works immediately in client-only mode when the local ZeroTier service is available. Open **Settings** and enter a Legacy Central API token only if hosted network and member management is required. The token is validated before replacing the current credential.

## Installing a release

Release files are published on the repository's **Releases** page.

### Arch Linux

Download the `.pacman` package and install it with:

```bash
sudo pacman -U ./ZeroTier-GUI-*.pacman
```

Alternatively, download the AppImage, make it executable, and run it without installing:

```bash
chmod +x ./ZeroTier-GUI-*.AppImage
./ZeroTier-GUI-*.AppImage
```

### Debian and Ubuntu

```bash
sudo apt install ./ZeroTier-GUI-*.deb
```

### Windows

Download the NSIS installer `.exe` for a normal installation, or the file containing `portable` when installation is not desired. Current builds are not code-signed, so Windows SmartScreen may display an unknown-publisher warning.

## Credential storage

Persistent storage is available only when Electron can use a secure operating-system encryption backend. Otherwise, the token remains in memory for the current process and is discarded when the application exits.

Tokens are never exposed to the renderer. Central requests are made in the main process through the selected Central provider.

## Local ZeroTier access on Linux

The graphical application should not run as root. ZeroTier normally restricts `/var/lib/zerotier-one/authtoken.secret`, which can prevent an ordinary desktop user from calling `zerotier-cli`.

The **Fix local access** action in Settings opens a system authorization prompt and performs two fixed operations when required:

1. Grants the signed-in user read access to the local ZeroTier service token using a per-user ACL.
2. Starts `zerotier-one.service` if it is not running.

No renderer-provided command, executable, username, or file path is passed to a shell. Access to the service token allows control of the local ZeroTier node, so it should be granted only to trusted desktop users.

## Architecture

```text
React renderer
    │  window.zerotier.central / window.zerotier.local
    ▼
Sandboxed preload bridge
    │  validated IPC messages
    ▼
Electron main process
    ├── ProviderStrategy
    │   ├── CentralV1Adapter ── Legacy Central API v1
    │   └── LocalCliAdapter ─── zerotier-cli
    ├── SecretStore
    └── SystemAppearance
```

The renderer depends only on the stable `central` and `local` contracts. `ProviderStrategy` currently selects `legacy-v1` and `zerotier-cli`. A future `CentralV2Adapter` can implement the same Central contract without changing application screens.

The renderer uses React without Redux or a component framework. Network members are requested only when a network details screen is opened, and there is no continuous polling loop.

## Platform appearance

- KDE Plasma: reads KDE colors and accent configuration and watches for changes.
- Windows and macOS: uses Electron native theme and system preference events.
- Other Linux desktops: uses Electron and XDG Desktop Portal appearance values where available.

## Current limitations

- Only Legacy Central personal tokens are supported.
- Client-only mode cannot discover remote members because `zerotier-cli` exposes local memberships, not the Central member directory. Ping accepts a target managed IP address manually.
- New Central v2 organizations, network groups, IAM, and service accounts are not implemented.
- Linux automatic access repair assumes a systemd-based ZeroTier installation and the standard service-token path.
- Windows packages are not code-signed.

## Releases

Pull requests targeting `main` run syntax checks, the renderer build, and the test suite. Packaging is intentionally not performed for branch pushes or pull requests.

After a pull request is merged, every relevant push to `main` builds AppImage, Debian, Arch Linux, Windows installer, and Windows portable artifacts. The workflow publishes them as an automated prerelease named `build-N`, following the same main-branch release model as Tendroid. Publication uses the repository-provided `GITHUB_TOKEN`; no additional release token is required.

## Contributing

Bug reports, UI feedback, and focused pull requests are welcome. Before submitting changes, run:

```bash
npm run check
npm test
```

# DNF AutoClean

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Fedora](https://img.shields.io/badge/Supported-Fedora%2038%2B-blue)](https://getfedora.org/)

A lightweight Fedora tool that automatically removes unused DNF packages and old kernels to keep systems lean.

## Features

- Removes unused DNF packages
- Keeps a configurable number of recent kernels (default: 2)
- Runs on a configurable schedule via systemd timer
- Simple configuration at `/etc/dnf-autoclean.conf`
- Installer script for quick setup

## Requirements

- Fedora 43 (or compatible)
- dnf available on the system
- systemd

## Installation

Clone and run the installer:

```bash
git clone https://github.com/brianrsmith1/dnf-autoclean.git
cd dnf-autoclean
chmod +x install.sh
./install.sh
```

Uninstall:

```bash
sudo dnf remove dnf-autoclean
```

## Configuration

Default config: `/etc/dnf-autoclean.conf`

Example:

```ini
[general]
retain_kernels = 2
schedule = weekly   # values: daily | weekly | monthly
```

- retain_kernels: number of recent kernels to keep
- schedule: how often the timer runs

## Usage

Run immediately:

```bash
sudo dnf-autoclean
```

Enable and start automatic runs:

```bash
sudo systemctl enable --now dnf-autoclean.timer
```

Check timer or service status:

```bash
systemctl status dnf-autoclean.timer
journalctl -u dnf-autoclean.service --no-pager
```

## Project Layout

- install.sh
- src/dnf-autoclean.sh
- man/dnf-autoclean.1
- packaging/dnf-autoclean.spec
- .github/workflows/build.yml
- LICENSE
- README.md

## Development

Build RPM:

```bash
rpmbuild -ba packaging/dnf-autoclean.spec
```

Run tests (if present):

```bash
./tests/run-tests.sh
```

## License

MIT — see LICENSE for details.

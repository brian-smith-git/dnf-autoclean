# DNF AutoClean

DNF AutoClean is a Fedora utility that:
- Removes old kernels (keeps the 3 most recent by default).
- Removes orphaned packages.
- Runs `dnf autoremove`.
- Provides a GTK GUI frontend.
- Integrates with systemd timers and polkit.

## Installation
```bash
git clone https://github.com/brian-smith-git/dnf-autoclean.git
cd dnf-autoclean
chmod +x install.sh
./install.sh

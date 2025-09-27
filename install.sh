#!/usr/bin/env bash


PREFIX="/opt/dnf-autoclean"
BIN="$PREFIX/dnf-autoclean.py"
GUI_BIN="/usr/bin/dnf-autoclean-gui"
SERVICE="/etc/systemd/system/dnf-autoclean.service"
TIMER="/etc/systemd/system/dnf-autoclean.timer"
POLKIT_ACTION="/usr/share/polkit-1/actions/org.briansmith.dnf-autoclean.policy"
POLKIT_RULE="/etc/polkit-1/rules.d/50-dnf-autoclean.rules"
DESKTOP="/usr/share/applications/dnf-autoclean.desktop"
ICON_DIR="/usr/share/icons/hicolor/128x128/apps"
ICON_PATH="$ICON_DIR/dnf-autoclean.png"
LOGFILE="/var/log/dnf-autoclean.log"


if [ "$EUID" -ne 0 ]; then
echo "Run as root: sudo $0"
exit 1
fi


echo "Installing DNF Auto Cleaner to $PREFIX"
mkdir -p "$PREFIX"
cp -v dnf-autoclean.py "$BIN"
chmod 755 "$BIN"


# Install GUI (if present)
if [ -f dnf-autoclean-gui.py ]; then
cp -v dnf-autoclean-gui.py "$GUI_BIN"
chmod 755 "$GUI_BIN"
fi


# Services
cp -v dnf-autoclean.service "$SERVICE"
cp -v dnf-autoclean.timer "$TIMER"


# Polkit
if [ -f org.briansmith.dnf-autoclean.policy ]; then
cp -v org.briansmith.dnf-autoclean.policy "$POLKIT_ACTION"
fi
if [ -f 50-dnf-autoclean.rules ]; then
cp -v 50-dnf-autoclean.rules "$POLKIT_RULE"
chmod 644 "$POLKIT_RULE"
fi


# Desktop + icon
install -d "$ICON_DIR"
if [ -f icon/dnf-autoclean.png ]; then
cp -v icon/dnf-autoclean.png "$ICON_PATH"
fi
cp -v dnf-autoclean.desktop "$DESKTOP"


# Ensure log exists
touch "$LOGFILE" || true
chmod 644 "$LOGFILE"


# Reload systemd & enable timer
systemctl daemon-reload
systemctl enable --now dnf-autoclean.timer


echo "Installation complete. Status of timer:"
systemctl status --no-pager dnf-autoclean.timer || true


echo "To test (dry-run): sudo $BIN --dry-run --keep 5"
echo "To run now (destructive): sudo $BIN --keep 5"


echo "Notes: The included

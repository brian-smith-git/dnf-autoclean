#!/bin/bash
set -e

echo "Installing dnf-autoclean..."

# Copy script
sudo cp dnf-autoclean.py /usr/bin/dnf-autoclean
sudo chmod +x /usr/bin/dnf-autoclean

# Copy systemd service and timer
sudo cp dnf-autoclean.service /etc/systemd/system/
sudo cp dnf-autoclean.timer /etc/systemd/system/

# Reload systemd daemons
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable --now dnf-autoclean.timer

echo "Installation complete. You can run 'sudo dnf-autoclean' manually or let the timer run it automatically."

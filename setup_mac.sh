#!/bin/bash

echo "=== Mac Setup for 24/7 Bot Running ==="

# Prevent sleep when laptop lid is closed (while plugged in)
echo "Setting power management - preventing sleep when plugged in..."
sudo pmset -c sleep 0
sudo pmset -c displaysleep 10
sudo pmset -c disksleep 0

# Keep system awake while on battery too (optional)
echo "Do you want to prevent sleep on battery too? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    sudo pmset -b sleep 0
    echo "Sleep disabled on battery too"
else
    echo "Sleep on battery unchanged"
fi

# Show current settings
echo "Current power management settings:"
pmset -g

echo "=== Setup complete! ==="
echo "Your laptop will now stay awake when plugged in, even with lid closed."
echo "To restore normal sleep: sudo pmset -c sleep 1"
#!/bin/bash

echo "=== Restoring Normal Sleep Settings ==="

# Restore normal sleep settings
sudo pmset -c sleep 1
sudo pmset -b sleep 1
sudo pmset -c displaysleep 1
sudo pmset -c disksleep 10

echo "Sleep settings restored to normal"
echo "Current settings:"
pmset -g

echo "=== Your laptop will now sleep normally when closed ==="
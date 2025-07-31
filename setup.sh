#!/bin/bash

# Simple installer to add 'shh' alias for SSH manager
# Place this script in the same directory as your Python script

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/shh.py"

# Check if Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: ssh-manager.py not found in $SCRIPT_DIR"
    echo "Please make sure the Python script is in the same directory as this installer."
    exit 1
fi

# Make Python script executable
chmod +x "$PYTHON_SCRIPT"

# Detect shell config file
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# Create the alias line
ALIAS_LINE="alias shh='$PYTHON_SCRIPT'"

# Check if alias already exists
if grep -q "alias shh=" "$SHELL_CONFIG" 2>/dev/null; then
    echo "Alias 'shh' already exists in $SHELL_CONFIG"
    echo "Current alias:"
    grep "alias shh=" "$SHELL_CONFIG"
    echo
    read -p "Replace it? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old alias and add new one
        sed -i '/alias shh=/d' "$SHELL_CONFIG"
        echo "$ALIAS_LINE" >> "$SHELL_CONFIG"
        echo "✓ Alias updated in $SHELL_CONFIG"
    else
        echo "Installation cancelled."
        exit 0
    fi
else
    # Add new alias
    echo "" >> "$SHELL_CONFIG"
    echo "# SSH Manager alias" >> "$SHELL_CONFIG"
    echo "$ALIAS_LINE" >> "$SHELL_CONFIG"
    echo "✓ Alias added to $SHELL_CONFIG"
fi

echo
echo "Installation complete!"
echo
echo "Usage:"
echo "  shh    # Launch SSH session manager"
echo
echo "To use immediately, run:"
echo "  source $SHELL_CONFIG"
echo "Or restart your terminal."
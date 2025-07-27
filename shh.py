#!/usr/bin/env python3

import subprocess
import sys
import re
from pathlib import Path

try:
    from pyfzf import FzfPrompt
    fzf = FzfPrompt()
except ImportError:
    print("Please install pyfzf: pip install pyfzf")
    print("Also ensure fzf is installed: sudo apt-get install fzf")
    sys.exit(1)

def get_ssh_history():
    ssh_sessions = set()
    
    history_files = [
        Path.home() / '.bash_history',
        Path.home() / '.zsh_history',
        Path.home() / '.history'
    ]
    
    ssh_pattern = re.compile(r'ssh\s+(?:-[^\s]+\s+)*([^@\s]+@[^\s]+)')
    
    for history_file in history_files:
        if history_file.exists():
            try:
                with open(history_file, 'r', errors='ignore') as f:
                    for line in f:
                        match = ssh_pattern.search(line)
                        if match:
                            session = match.group(1)
                            if '@' in session and len(session.split('@')) == 2:
                                ssh_sessions.add(session)
                                
                                user, host = session.split('@')
                                ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')

                                if not ip_pattern.match(host):

                                    try:
                                        result = subprocess.run(
                                            ['getent', 'hosts', host],
                                            capture_output=True,
                                            text=True,
                                            timeout=1
                                        )
                                        if result.returncode == 0 and result.stdout:
                                            ip = result.stdout.split()[0]
                                            ssh_sessions.add(f"{user}@{ip}")
                                    except:
                                        pass
            except:
                pass
    
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    if known_hosts.exists():
        try:
            with open(known_hosts, 'r', errors='ignore') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        parts = line.split()
                        if parts:
                            host_part = parts[0]
                            host_part = re.sub(r'^\[([^\]]+)\]:\d+$', r'\1', host_part)
                            if not host_part.startswith('|'):
                                for session in list(ssh_sessions):
                                    if '@' in session:
                                        user, existing_host = session.split('@')
                                        if existing_host == host_part or host_part in existing_host:
                                            ssh_sessions.add(f"{user}@{host_part}")
        except:
            pass
    
    # 3. Check SSH config file for hosts
    ssh_config = Path.home() / '.ssh' / 'config'
    if ssh_config.exists():
        try:
            with open(ssh_config, 'r') as f:
                current_host = None
                current_user = None
                current_hostname = None
                
                for line in f:
                    line = line.strip()
                    if line.startswith('Host ') and not line.startswith('Host *'):
                        current_host = line.split()[1]
                    elif line.startswith('User '):
                        current_user = line.split()[1]
                    elif line.startswith('HostName '):
                        current_hostname = line.split()[1]
                    
                    if current_user and current_hostname:
                        ssh_sessions.add(f"{current_user}@{current_hostname}")
                        if current_host:
                            ssh_sessions.add(f"{current_user}@{current_host}")
                    elif current_host and current_user:
                        ssh_sessions.add(f"{current_user}@{current_host}")
        except:
            pass
    
    try:
        result = subprocess.run(
            ['sudo', '-n', 'grep', 'sshd.*Accepted', '/var/log/auth.log'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                match = re.search(r'Accepted \w+ for (\w+) from ([\d.]+)', line)
                if match:
                    user, ip = match.groups()
                    ssh_sessions.add(f"{user}@{ip}")
    except:
        pass
    
    return sorted(list(ssh_sessions))

def check_ssh_service():
    """Check if SSH service is running properly"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'ssh'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip() != 'active':
            print("⚠️  SSH service is not active. You may want to check:")
            print("   sudo systemctl status ssh")
            print("   journalctl -u sshd")
            print()
    except:
        pass

def main():
    check_ssh_service()
    
    sessions = get_ssh_history()
    
    if not sessions:
        print("No SSH sessions found in history.")
        print("\nTip: SSH sessions are extracted from:")
        print("  - Shell history files (~/.bash_history, ~/.zsh_history)")
        print("  - SSH known_hosts file (~/.ssh/known_hosts)")
        print("  - SSH config file (~/.ssh/config)")
        sys.exit(1)
    
    try:
        selected = fzf.prompt(sessions, '--height 40% --reverse --prompt="Select SSH session: "')
        
        if selected:
            session = selected[0]
            print(f"Connecting to {session}...")
            
            subprocess.run(['ssh', session])
    
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
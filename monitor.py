import time
import psutil

from rich.live import Live
from rich.table import Table
from rich import box

def get_size(bytes):
    """Convert bytes to human-readable format (KB, MB, GB)"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"

def create_process_table():
    """Create and return a table for process information"""
    table = Table(box=box.SIMPLE)
    table.add_column("PID", justify="right")
    table.add_column("Name", no_wrap=True)
    table.add_column("CPU %", justify="right")
    table.add_column("Memory", justify="right")
    table.add_column("Status")
    table.add_column("User")
    return table

def get_process_cpu_usage():
    """Get CPU usage for all processes"""
    process_cpu = {}
    for proc in psutil.process_iter(['pid']):
        try:
            process_cpu[proc.info['pid']] = proc.cpu_percent(interval=0)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_cpu

def get_process_details(process_cpu):
    """Get details for all processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'status']):
        try:
            # Get process info
            process_info = proc.info
            pid = process_info['pid']
            cpu_percent = process_cpu.get(pid, 0)
            
            # Get memory usage
            memory_info = process_info['memory_info'] if 'memory_info' in process_info else None
            memory_usage = get_size(memory_info.rss) if memory_info else "N/A"
            
            processes.append({
                'pid': pid,
                'name': process_info.get('name', "N/A"),
                'username': process_info.get('username', "N/A"),
                'memory_usage': memory_usage,
                'cpu_percent': cpu_percent,
                'status': process_info.get('status', "N/A")
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort processes by CPU usage (highest first)
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes

def format_cpu_text(cpu_percent):
    """Format CPU text with color based on usage"""
    cpu_text = f"{cpu_percent:.1f}"
    if cpu_percent > 50:
        return f"[bold red]{cpu_text}[/]"
    elif cpu_percent > 20:
        return f"[bold yellow]{cpu_text}[/]"
    return f"[green]{cpu_text}[/]"

def format_status_text(status):
    """Format status text with color"""
    status_lower = status.lower()
    if status_lower == 'running':
        return f"[green]{status}[/]"
    elif status_lower == 'sleeping':
        return f"[blue]{status}[/]"
    elif status_lower in ['zombie', 'dead']:
        return f"[red]{status}[/]"
    return status

with Live(refresh_per_second=2, screen=False) as live:  # update 2 times a second
    while True:
        try:
            # Get CPU usage percentage for each process
            process_cpu = get_process_cpu_usage()
            
            # Give a short delay to allow CPU percent calculation to work
            time.sleep(0.5)
            
            # Create a new table each time to refresh data
            table = create_process_table()
            
            # Get process details and sort by CPU usage
            processes = get_process_details(process_cpu)
            
            # Show only top 20 processes
            for proc in processes[:20]:
                table.add_row(
                    str(proc['pid']),
                    proc['name'],
                    format_cpu_text(proc['cpu_percent']),
                    proc['memory_usage'],
                    format_status_text(proc['status']),
                    proc['username']
                )
            
            live.update(table)
            
        except KeyboardInterrupt:
            break

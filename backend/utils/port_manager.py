#!/usr/bin/env python3
"""
Port Management Utilities for ALwrity Backend
Handles port cleanup, conflict resolution, and management.
"""

import os
import sys
import socket
import subprocess
import time
from typing import Optional, List


def find_free_port(start_port=8000, max_attempts=10):
    """
    Find a free port starting from start_port.
    
    Args:
        start_port: Starting port number to search from
        max_attempts: Maximum number of ports to check
        
    Returns:
        int: First available port found
        
    Raises:
        RuntimeError: If no free ports found in range
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports found in range {start_port}-{start_port + max_attempts - 1}")


def is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
    except Exception:
        return False


def get_process_using_port(port: int) -> Optional[dict]:
    """Get information about the process using a specific port."""
    try:
        if sys.platform == "win32":
            # Windows: Use netstat
            result = subprocess.run(
                ['netstat', '-ano', '-p', 'tcp'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            # Get process info
                            proc_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            lines = proc_result.stdout.split('\n')
                            if len(lines) > 1:
                                proc_info = lines[1].strip('"').split('","')
                                if len(proc_info) >= 2:
                                    return {
                                        'pid': pid,
                                        'name': proc_info[0],
                                        'command': ' '.join(proc_info[1:]),
                                        'port': port
                                    }
                        except Exception:
                            pass
        
        else:
            # Unix/Linux/Mac: Use lsof
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 2:
                    return {
                        'pid': parts[1],
                        'name': parts[0],
                        'command': ' '.join(parts[8:]),
                        'port': port
                    }
    
    except Exception as e:
        print(f"Error checking port {port}: {e}")
    
    return None


def kill_process_on_port(port: int, force: bool = False) -> bool:
    """Kill the process using a specific port."""
    process_info = get_process_using_port(port)
    if not process_info:
        print(f"✅ Port {port} is not in use")
        return True
    
    print(f"🔍 Found process using port {port}:")
    print(f"   PID: {process_info['pid']}")
    print(f"   Name: {process_info['name']}")
    print(f"   Command: {process_info['command'][:100]}...")
    
    try:
        if sys.platform == "win32":
            # Windows: Use taskkill
            cmd = ['taskkill', '/PID', process_info['pid']]
            if force:
                cmd.append('/F')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Successfully terminated process {process_info['pid']}")
                return True
            else:
                print(f"❌ Failed to terminate process: {result.stderr}")
                return False
        
        else:
            # Unix/Linux/Mac: Use kill
            signal = 'SIGKILL' if force else 'SIGTERM'
            result = subprocess.run(
                ['kill', '-' + signal, process_info['pid']],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully terminated process {process_info['pid']}")
                return True
            else:
                print(f"❌ Failed to terminate process: {result.stderr}")
                return False
    
    except Exception as e:
        print(f"❌ Error killing process: {e}")
        return False


def wait_for_port_free(port: int, timeout: int = 10) -> bool:
    """Wait for a port to become free."""
    print(f"⏳ Waiting for port {port} to become free...")
    
    for i in range(timeout):
        if not is_port_in_use(port):
            print(f"✅ Port {port} is now free")
            return True
        time.sleep(1)
    
    print(f"⚠️  Port {port} still in use after {timeout} seconds")
    return False


def cleanup_port(port: int, force: bool = False, wait: bool = True) -> bool:
    """Clean up a port by killing the process using it."""
    print(f"🧹 Cleaning up port {port}...")
    
    if not is_port_in_use(port):
        print(f"✅ Port {port} is already free")
        return True
    
    # Kill the process
    success = kill_process_on_port(port, force)
    
    if success and wait:
        # Wait for port to become free
        wait_for_port_free(port)
    
    return success


def list_alwrity_ports() -> List[dict]:
    """List all ports currently used by ALwrity processes."""
    alwrity_ports = []
    
    # Check common ALwrity port range
    for port in range(8000, 8010):
        process_info = get_process_using_port(port)
        if process_info and ('python' in process_info['name'].lower() or 'alwrity' in process_info['command'].lower()):
            alwrity_ports.append(process_info)
    
    return alwrity_ports


def cleanup_all_alwrity_ports(force: bool = False) -> int:
    """Clean up all ALwrity processes."""
    ports = list_alwrity_ports()
    
    if not ports:
        print("✅ No ALwrity processes found running")
        return 0
    
    print(f"🔍 Found {len(ports)} ALwrity process(es):")
    for port_info in ports:
        print(f"   Port {port_info['port']}: PID {port_info['pid']} ({port_info['name']})")
    
    cleaned_count = 0
    for port_info in ports:
        print(f"\n🧹 Cleaning up port {port_info['port']}...")
        if cleanup_port(port_info['port'], force=force, wait=False):
            cleaned_count += 1
    
    if cleaned_count > 0:
        print(f"\n⏳ Waiting for ports to become free...")
        time.sleep(2)
    
    print(f"\n✅ Cleaned up {cleaned_count} ALwrity process(es)")
    return cleaned_count


def cleanup_port_if_needed(port: int, force: bool = False) -> bool:
    """Clean up port if it's in use by another ALwrity process."""
    if not is_port_in_use(port):
        return True
    
    print(f"⚠️  Port {port} is already in use")
    
    # Try to identify if it's an ALwrity process
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ['netstat', '-ano', '-p', 'tcp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            proc_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if 'python' in proc_result.stdout.lower():
                                print(f"🔍 Found Python process (PID: {pid}) using port {port}")
                                
                                if force:
                                    print(f"🧹 Force cleaning up port {port}...")
                                    subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                                capture_output=True, timeout=5)
                                    time.sleep(2)
                                    return not is_port_in_use(port)
                                else:
                                    print(f"💡 Use --cleanup-port to clean up, or --port <different-port>")
                                    return False
                        except Exception:
                            pass
        else:
            # Unix/Linux/Mac: Use lsof
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if 'python' in result.stdout.lower():
                print(f"🔍 Found Python process using port {port}")
                if force:
                    print(f"🧹 Force cleaning up port {port}...")
                    # Extract PID and kill
                    lines = result.stdout.split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 2:
                            pid = parts[1]
                            subprocess.run(['kill', '-9', pid], timeout=5)
                            time.sleep(2)
                            return not is_port_in_use(port)
                else:
                    print(f"💡 Use --cleanup-port to clean up, or --port <different-port>")
                    return False
    
    except Exception as e:
        print(f"Error checking port: {e}")
    
    return False


def interactive_port_cleanup():
    """Interactive port cleanup utility."""
    print("🧹 ALwrity Port Cleanup Utility")
    print("=" * 40)
    
    # List current ALwrity processes
    ports = list_alwrity_ports()
    
    if not ports:
        print("✅ No ALwrity processes found running")
        return
    
    print(f"\n🔍 Found {len(ports)} ALwrity process(es):")
    for i, port_info in enumerate(ports, 1):
        print(f"{i}. Port {port_info['port']}: PID {port_info['pid']} ({port_info['name']})")
        print(f"   Command: {port_info['command'][:80]}...")
    
    print(f"\nOptions:")
    print(f"1. Clean up specific port")
    print(f"2. Clean up all ALwrity ports")
    print(f"3. Force clean up all ports")
    print(f"4. Exit")
    
    try:
        choice = input(f"\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            port_num = input("Enter port number: ").strip()
            try:
                port = int(port_num)
                cleanup_port(port, force=False)
            except ValueError:
                print("❌ Invalid port number")
        
        elif choice == "2":
            cleanup_all_alwrity_ports(force=False)
        
        elif choice == "3":
            cleanup_all_alwrity_ports(force=True)
        
        elif choice == "4":
            print("👋 Exiting...")
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Exiting...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "cleanup":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else None
            if port:
                cleanup_port(port)
            else:
                cleanup_all_alwrity_ports()
        
        elif command == "list":
            ports = list_alwrity_ports()
            if ports:
                print(f"Found {len(ports)} ALwrity process(es):")
                for port_info in ports:
                    print(f"Port {port_info['port']}: PID {port_info['pid']}")
            else:
                print("No ALwrity processes found")
        
        elif command == "check":
            port = int(sys.argv[2])
            if is_port_in_use(port):
                process_info = get_process_using_port(port)
                if process_info:
                    print(f"Port {port} is in use by PID {process_info['pid']} ({process_info['name']})")
                else:
                    print(f"Port {port} is in use")
            else:
                print(f"Port {port} is free")
        
        else:
            print("Usage:")
            print("  python port_manager.py cleanup [port]  # Cleanup specific port or all")
            print("  python port_manager.py list           # List ALwrity processes")
            print("  python port_manager.py check <port>   # Check if port is in use")
    
    else:
        interactive_port_cleanup()

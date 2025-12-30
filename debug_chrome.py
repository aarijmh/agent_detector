#!/usr/bin/env python3
"""Debug script to check Chrome debugging port connectivity"""

import asyncio
import httpx
import subprocess
import sys

async def check_chrome_connection(port: int = 9222):
    """Check if Chrome is accessible on the debugging port"""
    print(f"Checking Chrome on port {port}...\n")
    
    # Check if port is listening
    print("1. Checking if port is listening...")
    result = subprocess.run(
        ["lsof", "-i", f":{port}"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"   ✓ Port {port} is listening")
        print(result.stdout)
    else:
        print(f"   ✗ Port {port} is NOT listening")
        print("   Chrome may not be running with --remote-debugging-port")
        return False
    
    # Try HTTP connection
    print(f"\n2. Trying HTTP connection to localhost:{port}...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://localhost:{port}/json/version")
            print(f"   ✓ HTTP connection successful (status: {response.status_code})")
            data = response.json()
            print(f"   Browser: {data.get('Browser', 'unknown')}")
            print(f"   Protocol: {data.get('Protocol-Version', 'unknown')}")
            ws_url = data.get("webSocketDebuggerUrl")
            if ws_url:
                print(f"   WebSocket URL: {ws_url}")
                return True
            else:
                print("   ✗ No webSocketDebuggerUrl in response")
                return False
    except Exception as e:
        print(f"   ✗ HTTP connection failed: {e}")
        return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
    success = asyncio.run(check_chrome_connection(port))
    sys.exit(0 if success else 1)

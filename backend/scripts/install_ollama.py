#!/usr/bin/env python3
"""
Ollama Installation Helper Script
This script helps install Ollama on different operating systems
"""

import os
import sys
import platform
import subprocess
import requests
from pathlib import Path

def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "linux":
        if "arm" in machine or "aarch64" in machine:
            return "linux-arm64"
        else:
            return "linux-amd64"
    elif system == "darwin":
        if "arm" in machine:
            return "macos-arm64"
        else:
            return "macos-amd64"
    elif system == "windows":
        return "windows-amd64"
    else:
        return "unknown"

def install_ollama_linux():
    """Install Ollama on Linux"""
    print("🐧 Installing Ollama on Linux...")
    
    try:
        # Download and install Ollama
        install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
        result = subprocess.run(install_cmd, shell=True, check=True, capture_output=True, text=True)
        
        print("✅ Ollama installed successfully!")
        print("💡 Starting Ollama service...")
        
        # Start Ollama service
        subprocess.run(["ollama", "serve"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("💡 Please install manually from: https://ollama.ai/download")
        return False
    except FileNotFoundError:
        print("❌ curl not found. Please install curl first:")
        print("   sudo apt-get install curl  # Ubuntu/Debian")
        print("   sudo yum install curl      # CentOS/RHEL")
        return False
    
    return True

def install_ollama_macos():
    """Install Ollama on macOS"""
    print("🍎 Installing Ollama on macOS...")
    
    try:
        # Check if Homebrew is installed
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
        
        # Install via Homebrew
        subprocess.run(["brew", "install", "ollama"], check=True)
        
        print("✅ Ollama installed successfully!")
        print("💡 Starting Ollama service...")
        
        # Start Ollama service
        subprocess.run(["ollama", "serve"], check=True)
        
    except subprocess.CalledProcessError:
        print("❌ Homebrew not found or installation failed")
        print("💡 Please install manually from: https://ollama.ai/download")
        return False
    except FileNotFoundError:
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    return True

def install_ollama_windows():
    """Install Ollama on Windows"""
    print("🪟 Installing Ollama on Windows...")
    
    print("📥 Please download and install Ollama from: https://ollama.ai/download")
    print("💡 After installation, run 'ollama serve' in a new terminal")
    
    # Check if Ollama is already installed
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        print("✅ Ollama is already installed!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama not found. Please install it manually.")
        return False

def check_ollama_installation():
    """Check if Ollama is properly installed"""
    try:
        result = subprocess.run(["ollama", "--version"], check=True, capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ Ollama is installed: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama is not installed or not in PATH")
        return False

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
            return True
        else:
            print("❌ Ollama is not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama is not running")
        return False

def main():
    """Main installation function"""
    print("🚀 Ollama Installation Helper")
    print("=" * 40)
    
    # Detect OS
    os_type = detect_os()
    print(f"🖥️ Detected OS: {os_type}")
    
    # Check if already installed
    if check_ollama_installation():
        if check_ollama_running():
            print("🎉 Ollama is already installed and running!")
            return True
        else:
            print("⚠️ Ollama is installed but not running")
            print("💡 Please run: ollama serve")
            return False
    
    # Install based on OS
    success = False
    if os_type.startswith("linux"):
        success = install_ollama_linux()
    elif os_type.startswith("macos"):
        success = install_ollama_macos()
    elif os_type.startswith("windows"):
        success = install_ollama_windows()
    else:
        print("❌ Unsupported operating system")
        print("💡 Please install manually from: https://ollama.ai/download")
        return False
    
    if success:
        print("\n🎉 Ollama installation completed!")
        print("💡 Next steps:")
        print("   1. Run: python backend/scripts/setup_ollama.py")
        print("   2. Test the installation")
    else:
        print("\n❌ Installation failed")
        print("💡 Please install manually from: https://ollama.ai/download")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

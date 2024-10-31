import os
import platform
import subprocess
import sys
import urllib.request
import zipfile
import tarfile

def install_cmake_windows():
    # URL for the CMake installer
    cmake_url = "https://github.com/Kitware/CMake/releases/latest/download/cmake-<latest_version>-win64-x64.msi"
    installer_path = "cmake_installer.msi"

    print("Downloading CMake for Windows...")
    urllib.request.urlretrieve(cmake_url, installer_path)

    print("Installing CMake...")
    subprocess.run(["msiexec", "/i", installer_path, "/quiet", "/norestart"], check=True)

    print("CMake installed successfully.")
    os.remove(installer_path)

def install_cmake_linux():
    print("Installing CMake for Linux...")
    # Update the package manager and install CMake
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "cmake", "-y"], check=True)
    print("CMake installed successfully.")

def install_cmake_macos():
    print("Installing CMake for macOS...")
    # Using Homebrew to install CMake
    if subprocess.call(["which", "brew"]) == 0:
        subprocess.run(["brew", "install", "cmake"], check=True)
    else:
        print("Homebrew is not installed. Please install Homebrew first.")
        sys.exit(1)
    print("CMake installed successfully.")

def main():
    os_type = platform.system()

    if os_type == "Windows":
        install_cmake_windows()
    elif os_type == "Linux":
        install_cmake_linux()
    elif os_type == "Darwin":  # macOS
        install_cmake_macos()
    else:
        print(f"Unsupported operating system: {os_type}")
        sys.exit(1)

if __name__ == "__main__":
    main()

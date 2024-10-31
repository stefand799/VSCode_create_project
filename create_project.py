import os
import json
import argparse
import platform

def create_directory_structure(project_name):
    # Directory paths
    directories = [
        project_name,
        f"{project_name}/include",  # Headers specific to the project
        f"{project_name}/src",      # Source files
        f"{project_name}/lib",      # External/third-party libraries
        f"{project_name}/build",    # Build output directory
        f"{project_name}/.vscode"   # VS Code settings
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def create_cmake_file(project_name, cpp_version):
    cmake_content = f"""cmake_minimum_required(VERSION 3.10)

# Project name and version
set(PROJECT_NAME {project_name})
project(${{PROJECT_NAME}} VERSION 1.0)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD {cpp_version})
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Include directories
include_directories(
    include                    # Include headers specific to the project
)

# Source files
file(GLOB SOURCES "src/*.cpp") # Source files

# Create executable
add_executable(${{PROJECT_NAME}} ${{SOURCES}})

# Platform-specific settings
if(MSVC)  # Check if using Microsoft Visual Studio
    message(STATUS "Configuring for Visual Studio")
elseif(UNIX)  # For Linux and macOS
    message(STATUS "Configuring for UNIX-based system")
    if(APPLE)  # Check if on macOS
        set(CMAKE_MACOSX_RPATH ON)
    endif()
endif()

# Output build info
message(STATUS "Project Name: {project_name}")
message(STATUS "C++ Standard: {cpp_version}")
"""

    # Write CMakeLists.txt to the project directory
    cmake_file_path = os.path.join(project_name, "CMakeLists.txt")
    with open(cmake_file_path, "w") as file:
        file.write(cmake_content)

def create_tasks_json(project_name):
    tasks_config = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "build",
                "type": "shell",
                "command": "cmake",
                "args": [
                    "--build",
                    ".",
                    "--config",
                    "Debug"
                ],
                "options": {
                    "cwd": "${workspaceFolder}/build"
                },
                "group": {
                    "kind": "build",
                    "isDefault": True
                },
                "problemMatcher": ["$gcc"]
            }
        ]
    }
    
    tasks_file_path = os.path.join(project_name, ".vscode", "tasks.json")
    with open(tasks_file_path, "w") as file:
        json.dump(tasks_config, file, indent=4)

def create_launch_json(project_name):
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "C++ Launch",
                "type": "cppdbg",
                "request": "launch",
                "program": "${workspaceFolder}/build/${workspaceFolderBasename}",
                "args": [],
                "stopAtEntry": False,
                "cwd": "${workspaceFolder}",
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",  # Use gdb for debugging
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    }
                ],
                "preLaunchTask": "build",
                "miDebuggerPath": "/usr/bin/gdb",  # Users should update this if different
            }
        ]
    }
    
    launch_file_path = os.path.join(project_name, ".vscode", "launch.json")
    with open(launch_file_path, "w") as file:
        json.dump(launch_config, file, indent=4)

def create_c_cpp_properties_json(project_name):
    system = platform.system()
    c_cpp_properties = {
        "configurations": [],
        "version": 4
    }

    if system == "Windows":
        c_cpp_properties["configurations"].append({
            "name": "Win32",
            "includePath": ["${workspaceFolder}/**",
                            "${workspaceFolder}/include/**"],
            "defines": [],
            "compilerPath": "g++",  # Update this to your MinGW path if necessary
            "cStandard": "c11",
            "cppStandard": "c++20",
            "intelliSenseMode": "windows-gcc-x64"
        })
    elif system == "Linux":
        c_cpp_properties["configurations"].append({
            "name": "Linux",
            "includePath": ["${workspaceFolder}/**",
                            "${workspaceFolder}/include/**"],
            "defines": [],
            "compilerPath": "/usr/bin/gcc",
            "cStandard": "c11",
            "cppStandard": "c++20",
            "intelliSenseMode": "linux-gcc-x64"
        })
    elif system == "Darwin":  # macOS
        c_cpp_properties["configurations"].append({
            "name": "macOS",
            "includePath": ["${workspaceFolder}/**",
                            "${workspaceFolder}/include/**"],
            "defines": [],
            "compilerPath": "/usr/local/bin/gcc",
            "cStandard": "c11",
            "cppStandard": "c++20",
            "intelliSenseMode": "macos-clang-x64"
        })

    c_cpp_properties_path = os.path.join(project_name, ".vscode", "c_cpp_properties.json")
    with open(c_cpp_properties_path, "w") as file:
        json.dump(c_cpp_properties, file, indent=4)

def create_detection_script(project_name):
    detection_script_content = """import os
import json
import platform

def find_compiler_and_update_configs():
    system = platform.system()
    paths = {}

    if system == "Windows":
        mingw_path = os.path.join(os.environ.get('PROGRAMFILES', ''), 'mingw-w64', 'x86_64-<your_mingw_path>', 'bin', 'g++.exe')
        vs_path = os.path.join(os.environ.get('PROGRAMFILES', ''), 'Microsoft Visual Studio', '2019', 'Community', 'VC', 'Tools', 'x64', 'bin', 'cl.exe')

        if os.path.isfile(mingw_path):
            paths['compilerPath'] = mingw_path
            paths['miDebuggerPath'] = os.path.join(os.path.dirname(mingw_path), 'gdb.exe')
        elif os.path.isfile(vs_path):
            paths['compilerPath'] = vs_path
            paths['miDebuggerPath'] = vs_path
        else:
            print("No suitable compiler found. Please install MinGW or Visual Studio.")
            return None

    elif system == "Linux":
        paths['compilerPath'] = "/usr/bin/g++"
        paths['miDebuggerPath'] = "/usr/bin/gdb"

        if not os.path.isfile(paths['compilerPath']):
            print(f"Compiler not found at {paths['compilerPath']}. Please ensure g++ is installed.")
            return None
        if not os.path.isfile(paths['miDebuggerPath']):
            print(f"Debugger not found at {paths['miDebuggerPath']}. Please ensure gdb is installed.")
            return None

    elif system == "Darwin":
        paths['compilerPath'] = "/usr/local/bin/g++"
        paths['miDebuggerPath'] = "/usr/bin/lldb"

        if not os.path.isfile(paths['compilerPath']):
            print(f"Compiler not found at {paths['compilerPath']}. Please ensure g++ is installed.")
            return None
        if not os.path.isfile(paths['miDebuggerPath']):
            print(f"Debugger not found at {paths['miDebuggerPath']}. Please ensure lldb is installed.")
            return None

    else:
        print("Unsupported operating system.")
        return None

    update_json_configs(system, paths)

def update_json_configs(system, paths):
    project_dir = os.getcwd()  # Get the current working directory
    vscode_dir = os.path.join(project_dir, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)  # Ensure .vscode directory exists

    # Update c_cpp_properties.json
    c_cpp_properties = {
        "configurations": [],
        "version": 4
    }

    if system == "Windows":
        c_cpp_properties["configurations"].append({
            "name": "Win32",
            "includePath": ["${workspaceFolder}/**",
                            "${workspaceFolder}/include/**"],
            "defines": [],
            "compilerPath": paths['compilerPath'],
            "cStandard": "c11",
            "cppStandard": "c++20",
            "intelliSenseMode": "windows-gcc-x64"
        })
    elif system == "Linux":
        c_cpp_properties["configurations"].append({
            "name": "Linux",
            "includePath": ["${workspaceFolder}/**",
                            "${workspaceFolder}/include/**"],
            "defines": [],
            "compilerPath": paths['compilerPath'],
            "cStandard": "c11",
            "cppStandard": "c++20",
            "intelliSenseMode": "linux-gcc-x64"
        })
    elif system == "Darwin":
        c_cpp_properties["configurations"].append({
            "name": "macOS",
            "includePath": ["${workspaceFolder}/**",
                            "${workspaceFolder}/include/**"],
            "defines": [],
            "compilerPath": paths['compilerPath'],
            "cStandard": "c11",
            "cppStandard": "c++20",
            "intelliSenseMode": "macos-clang-x64"
        })

    with open(os.path.join(vscode_dir, "c_cpp_properties.json"), "w") as file:
        json.dump(c_cpp_properties, file, indent=4)

if __name__ == "__main__":
    find_compiler_and_update_configs()
"""

    detection_script_path = os.path.join(project_name, "configure_project.py")
    with open(detection_script_path, "w") as file:
        file.write(detection_script_content)

def create_main_cpp(project_name):
    main_cpp_content = """#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""

    main_cpp_path = os.path.join(project_name, "src", "main.cpp")
    with open(main_cpp_path, "w") as file:
        file.write(main_cpp_content)

def main():
    parser = argparse.ArgumentParser(description="Create a C++ project structure.")
    parser.add_argument("project_name", help="The name of the project to create")
    parser.add_argument("--cpp-version", type=int, default=20, help="The C++ version to use (e.g., 20)")
    
    args = parser.parse_args()

    # Create project directory structure
    create_directory_structure(args.project_name)
    
    # Create CMake file
    create_cmake_file(args.project_name, args.cpp_version)
    
    # Create VS Code configuration files
    create_tasks_json(args.project_name)
    create_launch_json(args.project_name)
    create_c_cpp_properties_json(args.project_name)

    # Create main.cpp file
    create_main_cpp(args.project_name)

    # Create a script for detecting and configuring the project based on OS
    create_detection_script(args.project_name)

    print(f"Project '{args.project_name}' created successfully!")

if __name__ == "__main__":
    main()

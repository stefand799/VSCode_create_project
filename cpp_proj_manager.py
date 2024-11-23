import os
import subprocess
import platform
import re

def detect_os():
    """Detect the current operating system."""
    if os.name == "nt":
        return "Windows"
    elif os.name == "posix":
        if "darwin" in platform.system().lower():
            return "macOS"
        else:
            return "Linux"
    else:
        return "Unknown"

def extract_version(output):
    """Extract version information from the tool's version output using regex."""
    version_pattern = r"\b(\d+\.\d+\.\d+|\d+\.\d+|\d+)\b"
    match = re.search(version_pattern, output)
    if match:
        return match.group(0)
    else:
        return None

def check_tool(tool_name, check_command):
    try:
        result = subprocess.run(check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        version_output = result.stdout or result.stderr
        version = extract_version(version_output)
        return {
            "name": tool_name,
            "found": True,
            "version": version or "Unknown",
            "message": f"{tool_name} is installed. Version: {version or 'Unknown'}"
        }
    except FileNotFoundError:
        return {
            "name": tool_name,
            "found": False,
            "version": None,
            "message": f"{tool_name} is not installed."
        }

def find_tool_path(tool_name):
    os_type = detect_os()
    try:
        if os_type == "Windows":
            result = subprocess.run(["where", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif os_type in ["Linux", "macOS"]:
            result = subprocess.run(["which", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            return None
        tool_path = result.stdout.strip()
        return tool_path if tool_path else None
    except subprocess.CalledProcessError as e:
        print(f"Error finding {tool_name}: {e}")
        return None

def check_all_tools():
    os_type = detect_os()
    tools_to_check = []
    if os_type == "Windows":
        tools_to_check = [
            {"name": "CMake", "check_command": ["cmake", "--version"]},
            {"name": "MSVC", "check_command": ["cl"]},
            {"name": "GDB", "check_command": ["gdb", "--version"]},
        ]
    elif os_type == "macOS" or os_type == "Linux":
        tools_to_check = [
            {"name": "CMake", "check_command": ["cmake", "--version"]},
            {"name": "GCC", "check_command": ["gcc", "--version"]},
            {"name": "G++", "check_command": ["g++", "--version"]},
            {"name": "GDB", "check_command": ["gdb", "--version"]},
        ]
    else:
        print("Unknown operating system detected.")
        return

    compilers_found = False
    debuggers_found = False
    cmake_found = False
    missing_tools = []

    for tool in tools_to_check:
        result = check_tool(tool["name"], tool["check_command"])
        print(result["message"])
        if tool["name"] in ["GCC", "G++", "MSVC"] and result["found"]:
            compilers_found = True
        if tool["name"] in ["GDB"] and result["found"]:
            debuggers_found = True
        if tool["name"] == "CMake" and result["found"]:
            cmake_found = True
        if not result["found"]:
            missing_tools.append(tool["name"])

    return compilers_found, debuggers_found, cmake_found, missing_tools

def create_project_structure(project_name, os_type, compilers_found, debuggers_found, cmake_found):
    """Create a basic C++ project structure."""
    try:
        os.makedirs(project_name, exist_ok=True)
        os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "include"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "build"), exist_ok=True)
        os.makedirs(os.path.join(project_name, ".vscode"), exist_ok=True)

        # Create a sample main.cpp file
        main_cpp_path = os.path.join(project_name, "src", "main.cpp")
        with open(main_cpp_path, "w") as main_cpp_file:
            main_cpp_file.write("""
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
""")

        # Create a CMakeLists.txt file only if CMake is found
        if cmake_found:
            cmake_lists_path = os.path.join(project_name, "CMakeLists.txt")
            with open(cmake_lists_path, "w") as cmake_file:
                cmake_file.write(f"""
cmake_minimum_required(VERSION 3.10)
project({project_name})

set(CMAKE_CXX_STANDARD 17)

# Add source files
file(GLOB_RECURSE SOURCES "src/*.cpp")

add_executable({project_name} ${{SOURCES}})
""")

        # Create VSCode configuration files
        create_vscode_config_files(project_name, os_type, compilers_found, debuggers_found)
        
        print(f"Project '{project_name}' structure created successfully.")
    except Exception as e:
        print(f"Error creating project structure: {e}")

def create_vscode_config_files(project_name, os_type, compilers_found, debuggers_found):
    """Create VSCode configuration files for debugging, building, and IntelliSense."""
    vscode_folder = os.path.join(project_name, ".vscode")
    
    # Create launch.json for debugging if debugger is found
    if debuggers_found:
        launch_json_path = os.path.join(vscode_folder, "launch.json")
        debugger_path = find_tool_path('gdb') if os_type in ["Linux", "macOS"] else ""
        with open(launch_json_path, "w") as launch_file:
            launch_file.write(f"""
{{
    "version": "0.2.0",
    "configurations": [
        {{
            "name": "(gdb) Launch",
            "type": "cppdbg",
            "request": "launch",
            "program": "${{workspaceFolder}}/build/{project_name}",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${{workspaceFolder}}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {{
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }}
            ],
            "preLaunchTask": "build",
            "miDebuggerPath": "{debugger_path}"
        }}
    ]
}}
""")

    # Create tasks.json for building if CMake is found
    if compilers_found and cmake_found:
        tasks_json_path = os.path.join(vscode_folder, "tasks.json")
        with open(tasks_json_path, "w") as tasks_file:
            tasks_file.write(f"""
{{
    "version": "2.0.0",
    "tasks": [
        {{
            "label": "build",
            "type": "shell",
            "command": "cmake --build build",
            "group": {{
                "kind": "build",
                "isDefault": true
            }},
            "problemMatcher": ["$gcc"],
            "detail": "Generated task for building the project."
        }}
    ]
}}
""")

    # Create settings.json for configuring VSCode workspace settings
    settings_json_path = os.path.join(vscode_folder, "settings.json")
    with open(settings_json_path, "w") as settings_file:
        settings_file.write("""
{
    "cmake.sourceDirectory": "${workspaceFolder}",
    "C_Cpp.intelliSenseEngine": "Default",
    "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools"
}
""")

    # Create c_cpp_properties.json for IntelliSense configurations if compiler is found
    if compilers_found:
        c_cpp_properties_path = os.path.join(vscode_folder, "c_cpp_properties.json")
        compiler_path = find_tool_path('g++') if os_type in ["Linux", "macOS"] else find_tool_path('cl')
        with open(c_cpp_properties_path, "w") as cpp_properties_file:
            cpp_properties_file.write(f"""
{{
    "configurations": [
        {{
            "name": "{os_type}",
            "includePath": [
                "${{workspaceFolder}}/include",
                "${{workspaceFolder}}/src"
            ],
            "defines": [],
            "compilerPath": "{compiler_path}",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "{os_type.lower()}-gcc-x64" if os_type in ["Linux", "macOS"] else "windows-msvc-x64"
        }}
    ],
    "version": 4
}}
""")

def edit_project_configurations(project_path):
    """Edit existing project configurations to match the current device setup."""
    vscode_folder = os.path.join(project_path, ".vscode")
    
    # Update c_cpp_properties.json with the correct compiler path
    c_cpp_properties_path = os.path.join(vscode_folder, "c_cpp_properties.json")
    if os.path.exists(c_cpp_properties_path):
        with open(c_cpp_properties_path, "r+") as cpp_properties_file:
            config = cpp_properties_file.read()
            compiler_path = find_tool_path('g++') if detect_os() in ["Linux", "macOS"] else find_tool_path('cl')
            config = re.sub(r'"compilerPath":\s*".*?"', f'"compilerPath": "{compiler_path}"', config)
            cpp_properties_file.seek(0)
            cpp_properties_file.write(config)
            cpp_properties_file.truncate()

    # Update launch.json to match the current debugger path
    launch_json_path = os.path.join(vscode_folder, "launch.json")
    if os.path.exists(launch_json_path):
        with open(launch_json_path, "r+") as launch_file:
            config = launch_file.read()
            debugger_path = find_tool_path('gdb') if detect_os() in ["Linux", "macOS"] else ""
            config = re.sub(r'"miDebuggerPath":\s*".*?"', f'"miDebuggerPath": "{debugger_path}"', config)
            launch_file.seek(0)
            launch_file.write(config)
            launch_file.truncate()

def main():
    # First functionality: Check OS, check tools, and give options to user
    compilers_found, debuggers_found, cmake_found, missing_tools = check_all_tools()
    os_type = detect_os()

    if compilers_found and debuggers_found and cmake_found:
        while True:
            print("\nOptions:")
            print("1. Create a new project")
            print("2. Edit existing project configuration")
            print("3. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                project_name = input("Enter the name of the new project: ")
                create_project_structure(project_name, os_type, compilers_found, debuggers_found, cmake_found)
            elif choice == "2":
                project_path = input("Enter the path of the existing project: ")
                edit_project_configurations(project_path)
            elif choice == "3":
                print("Exiting script.")
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        for tool in missing_tools:
            print(f"Please install the missing tool: {tool}")

if __name__ == "__main__":
    main()

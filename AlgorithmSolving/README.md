# Algorithm Solving Environment

## 📋 Overview

This environment is configured for efficient algorithm problem solving

## 🔧 Features

### Test Case Management

- Automatically creates test case directories
- Handles input/output file redirection
- Supports multiple test cases per problem

### Build System

- CMake-based build configuration
- Automatic executable generation
- Debug and Release modes support

### VS Code Integration

- Pre-configured C++ IntelliSense
- Integrated debugging setup
- Custom build tasks
- Preconfigured bits/stdc++.h header

## 📦 Directory Structure

```
AlgorithmSolving/
├── .vscode/                  # VS Code configuration
│   ├── bits/                 # Precompiled headers
│   ├── c_cpp_properties.json # C++ configuration
│   ├── launch.json          # Debug configuration
│   ├── settings.json        # Editor settings
│   └── tasks.json           # Build tasks
├── CMakeLists.txt           # CMake configuration
└── .gitignore               # Git ignore rules
```

## 🚀 Getting Started

1. Install Prerequisites:

   - MinGW G++ Compiler
   - CMake
   - VS Code with C/C++ extension

2. Setup Project:

   - Copy this directory to your workspace
   - Open in VS Code
   - CMake will configure automatically

3. Create New Solution:
   - Create a new .cpp file in Solutions directory
   - Build using Ctrl+Shift+B
   - Debug using F5

## ⚙️ Configuration

### Compiler Settings

- C++17 standard enabled
- UTF-8 encoding
- Optimization flags for different build types

### VS Code Settings

- Format on save enabled
- Custom snippet support
- Integrated terminal configuration

## 🔍 Usage Tips

1. Test Case Management:

   ```cpp
   // Input from file
   freopen("input.txt", "r", stdin);
   // Output to file
   freopen("output.txt", "w", stdout);
   ```

2. Debug Configuration:
   - Breakpoints supported
   - Variable inspection
   - Console I/O redirection

## 🤝 Contributing

Feel free to suggest improvements or report issues.

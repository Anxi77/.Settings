# Baekjoon Problem Logging System

[English](README.en.md) | [한국어](README.md)

## 📋 Overview

This system automatically generates and updates a README with solved Baekjoon Online Judge (BOJ) problems, categorizing them by algorithms and difficulty levels.

## 🔧 Features

### Problem Tracking

- Automatically detects solved problems
- Categorizes by algorithm types
- Tracks difficulty levels
- Maintains problem statistics

### API Integration

- Integrates with solved.ac API
- Fetches problem metadata
- Retrieves difficulty ratings
- Gets problem tags and categories

### GitHub Actions

- Automatic README updates
- Triggers on solution commits
- Maintains difficulty statistics
- Generates problem indexes

## 📦 Directory Structure

```
BaekjoonLogging/
├── Algo_Readme_Action.py     # Main script
├── update-readme.yml         # GitHub Actions workflow
└── README.md                # Documentation
```

## ⚙️ Configuration

### GitHub Actions Setup

```yaml
name: Update README
on:
  push:
    paths:
      - "Solutions/**" # Triggers on solution updates
      - ".github/scripts/**" # Triggers on script updates
```

### Script Configuration

- Problem difficulty emojis
- Category organization
- File path patterns
- API request settings

## 🔍 Generated Content

1. Difficulty Statistics:

   - Bronze to Ruby levels
   - Total problem count
   - Category-wise breakdown

2. Problem Categories:
   - Algorithm type grouping
   - Difficulty indicators
   - Links to solutions
   - Implementation tests

## 🚀 Usage

1. Solution Structure:

   ```
   Solutions/
   └── Baekjoon/
       └── [Problem Number]/
           └── [Problem Number].cpp
   ```

2. Automatic Updates:
   - Commit solutions to the repository
   - GitHub Actions automatically runs
   - README updates with new problems

## 🤝 Contributing

Feel free to suggest improvements or report issues.

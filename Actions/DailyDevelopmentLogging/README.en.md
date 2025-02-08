# Daily Development Log Action Guide

[English](README.en.md) | [한국어](README.md)

## 📌 Overview

This GitHub Action automatically generates and manages daily development logs based on commit messages. It helps systematically manage work history and TODO items by branch.

## 🔧 Key Features

1. **Automatic Daily Development Log Generation**

   - Auto-creates development log issues for the current date
   - Organizes commit history by branch
   - Manages TODO items

2. **Branch Management**

   - Accumulates commit history by branch
   - Displays commit details (time, author, type)
   - Links related issues

3. **TODO Management**
   - Manages TODO items in checkbox format
   - Automatically transfers incomplete TODOs from previous dates
   - Preserves TODO status (complete/incomplete)
   - Handles duplicate TODOs

## 💫 Commit Message Format

Commit messages should follow this format:

```
[type] title

[Body]
Write detailed content here.
Multiple lines are supported.

[Todo]
- New TODO item 1
- New TODO item 2

[Footer]
#related-issue #tags
```

### Commit Types

- `feat`: ✨ New feature
- `fix`: 🐛 Bug fix
- `refactor`: ♻️ Code refactoring
- `docs`: 📝 Documentation update
- `test`: ✅ Test code
- `chore`: 🔧 Build/config changes
- `style`: 💄 Code style changes
- `perf`: ⚡️ Performance improvements

## ⚙️ Configuration

You can modify the following settings in `.github/workflows/create-issue-from-commit.yml`:

```yaml
env:
  TIMEZONE: "Asia/Seoul" # Timezone setting
  ISSUE_PREFIX: "📅" # Issue title prefix
  ISSUE_LABEL: "daily-log" # Default label
  EXCLUDED_COMMITS: "^(chore|docs|style):" # Commit types to exclude
```

## 📋 Auto-generated Issue Format

```markdown
# 📅 Daily Development Log (YYYY-MM-DD) - Repository Name

<div align="center">

## 📊 Branch Summary

</div>

<details>
<summary><h3>✨ Branch Name</h3></summary>
Detailed commit content
</details>

<div align="center">

## 📝 Todo

</div>

- [ ] TODO item 1
- [x] TODO item 2 (completed)
```

## 🔍 Debug Output

The action outputs the following information during execution:

1. Current issue's TODO list
2. TODO item statistics
3. Newly added TODO list
4. TODOs transferred from previous dates
5. Final results

## ⚠️ Important Notes

1. Please strictly follow the commit message format
2. TODO items must start with `-` or `*`
3. Previous date's issues are automatically closed
4. Commits of type `chore`, `docs`, and `style` are excluded by default

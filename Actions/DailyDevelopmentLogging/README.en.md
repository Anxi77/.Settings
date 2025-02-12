# Daily Development Log Action Guide

[English](README.en.md) | [한국어](README.md)

## 📌 Overview

This GitHub Action automatically generates and manages daily development logs based on commit messages. It helps systematically manage work history and TODO items by branch.

## 🔧 Key Features

1. **Automatic Daily Development Log**

   - Auto-generation of daily development log issues
   - Branch-wise commit history organization
   - TODO item management

2. **Branch Management**

   - Cumulative commit history by branch
   - Detailed commit information (time, author, type)
   - Issue linking

3. **TODO Management**
   - Checkbox-style TODO item management
   - Automatic migration of incomplete TODOs
   - TODO status preservation (complete/incomplete)
   - Duplicate TODO handling
   - Automatic category statistics (e.g., General (5/10))
   - Automatic issue creation

## 💫 Commit Message Format

Commit messages should follow this format:

```
[type] title

[Body]
Write detailed content here.
Multiple lines are supported.

[Todo]
@Category1
- Todo item for category 1
- Another todo item for category 1

@Category2
- Todo item for category 2

- Uncategorized todo item (goes to General category)
- Another uncategorized todo item

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

### Todo Category Features

#### 1. Category Creation and Management

- Create new categories using `@CategoryName` format
- Case-insensitive category handling (`@FEATURE` and `@Feature` are treated as the same category)
- Original category case is preserved in display
- Uncategorized items automatically go to 'General' category

#### 2. Category Statistics

- Automatic calculation of completed/total items per category
- Statistics displayed in `CategoryName (completed/total)` format
- Real-time statistics updates
- Automatic cleanup of empty categories

#### 3. Automatic Issue Creation

- Convert TODO items to issues using `(issue)` prefix
- Automatic category label addition
- Automatic linking with daily development log
- Original TODO item replaced with issue number upon creation

### Todo Section Usage Examples

1. **Basic Category Usage**

```markdown
@Feature

- Implement new functionality
- Improve existing feature

@Bug

- Fix bug
- (issue) Critical bug discovered
```

2. **Automatic Issue Creation**

```markdown
- (issue) Performance optimization needed #123
```

↓ After conversion

```markdown
- #124 (automatically generated issue number)
```

3. **Category Statistics Display**

```markdown
<details>
<summary>📑 Feature (1/2)</summary>
- [ ] Implement new functionality
- [x] Improve existing feature
</details>

<details>
<summary>📑 Bug (0/2)</summary>
- [ ] Fix bug
- [ ] #124
</details>
```

### Best Practices

1. **Category Organization**

   - Organize categories by project areas
   - Group related tasks together
   - Use consistent category naming conventions

2. **Issue Creation**

   - Create issues only for important or trackable items
   - Include clear descriptions with issues
   - Create issues from relevant categories

3. **Statistics Usage**
   - Monitor progress using statistics
   - Track category workload
   - Monitor incomplete items

### Important Notes

1. **Category Management**

   - Avoid creating too many categories
   - Use meaningful category names
   - Maintain consistent category structure

2. **Issue Creation**

   - Avoid duplicate issue creation
   - Provide appropriate context and description
   - Utilize issue linking

3. **Statistics Management**
   - Regular completion status checks
   - Clean up old items
   - Monitor progress through statistics

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

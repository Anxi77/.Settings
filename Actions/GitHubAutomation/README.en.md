# GitHub Automation System

[English](README.en.md) | [한국어](README.md)

---

## 📌 Overview

Complete GitHub automation system for commit tracking, task management, and project reporting. Fully integrated with GitHub Issues and Project boards to provide comprehensive project management.

### ✨ Key Features
- **Complete GraphQL API Integration** - Built on latest GitHub GraphQL API
- **Automatic Daily Status Report (DSR) Generation** - Commit-based automated reports
- **Project Board Synchronization** - Real-time issue and task status management
- **Smart Commit Parsing** - Full support for [type] format commit messages
- **Label Management Automation** - Automatic label updates based on issue status
- **Comprehensive Validation System** - Automated validation of all components

## 🚀 Quick Setup

### 1. Copy Files
```bash
# Copy entire .github structure to your repository
cp -r Actions/GitHubAutomation/.github/* .github/
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r .github/scripts/requirements.txt
```

### 3. Configure GitHub Secrets
In Repository Settings → Secrets and variables → Actions, configure:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API token (repo, project permissions) | ✅ |

### 4. Setup Project Board
Create a project board in GitHub Repository → Projects and set the project number in `config.yaml`.

## 🔧 Detailed Features

### 📅 Automatic DSR (Daily Status Report) Generation
- **Commit-based Auto Generation**: Analyzes daily commits and automatically creates DSR issues
- **TODO Item Tracking**: Automatically extracts TODO items from commit message Todo sections
- **Previous TODO Migration**: Automatically migrates incomplete TODOs to next day's DSR
- **Branch-wise Classification**: Classifies commits by branch for organized reports
- **Smart Filtering**: Configured commit type exclusion and automated bot filtering

### 📊 Project Board Synchronization
- **Real-time Issue Sync**: Complete synchronization between GitHub Issues and Project V2 boards
- **Automatic Field Updates**: Automatic management of status, priority, and category fields
- **Label-based Classification**: Automatic task classification based on issue labels
- **Batch Updates**: Performance optimization through efficient GraphQL batch operations
- **Statistics Generation**: Automatic calculation of project progress and completion rates

### 🏷️ Label Management Automation
- **Status Label Sync**: Automatic label updates when task status changes
- **Priority Management**: Management of priority:high, priority:medium, etc. priority labels
- **Category Classification**: Automatic category classification through category: prefix
- **Smart Label Replacement**: Remove existing status labels and apply new ones

### 📈 Project Reporting
- **Comprehensive Statistics**: Task completion rates, status distribution, priority distribution
- **Performance Metrics**: API usage, processing time, success rate, and other operational metrics
- **Status Monitoring**: System health checks and component validation
- **Automated Reports**: Regular automated project progress reports

## ⚙️ Configuration

### Basic Configuration (`config.yaml`)
```yaml
# Global Settings
global:
  timezone: "Asia/Seoul"          # Timezone setting
  project_number: 2               # GitHub project number
  max_retries: 3                  # API retry count
  log_level: "INFO"               # Logging level

# DSR Settings
daily_reporter:
  enabled: true                   # Enable DSR generation
  issue_prefix: "📅"             # DSR issue title prefix
  dsr_label: "DSR"               # DSR issue label
  branch_label_prefix: "branch:" # Branch label prefix
  excluded_commit_types:          # Commit types to exclude
    - "chore"
    - "docs" 
    - "style"
  keep_dsr_days: 7               # DSR retention period

# Project Sync Settings
project_sync:
  enabled: true                  # Enable project synchronization
  status_field_name: "Status"   # Status field name
  priority_field_name: "Priority" # Priority field name
  category_field_name: "Category" # Category field name
  
  # Status label mappings
  status_labels:
    "todo": "TODO"
    "in-progress": "IN_PROGRESS"
    "in-review": "IN_REVIEW" 
    "done": "DONE"
    "blocked": "BLOCKED"
  
  # Priority label mappings
  priority_labels:
    "priority:low": "LOW"
    "priority:medium": "MEDIUM"
    "priority:high": "HIGH"
    "priority:critical": "CRITICAL"

# GitHub API Settings
github:
  max_retries: 3                 # Maximum retry attempts
  base_delay: 1.0               # Base delay time
  rate_limit_buffer: 100        # Rate limit buffer

# Logging Settings
logging:
  level: "INFO"                 # Logging level
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

### Environment-specific Settings
```yaml
environments:
  development:
    log_level: "DEBUG"
    max_retries: 1
    
  production:
    log_level: "WARNING"
    max_retries: 3
    notification_on_critical_error: true
```

## 📝 Commit Convention Guide

This system uses structured commit messages in **[type] format**.

### Basic Structure
```
[type(scope)] commit title

[Body]
Detailed description
- Change 1
- Change 2

[Todo]
@category
- TODO item 1
- TODO item 2

[Footer]
Issue references and metadata
- Closes #123
- Related to #124, #125
```

### Supported Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `[feat] add user authentication system` |
| `fix` | Bug fix | `[fix] resolve login error` |
| `docs` | Documentation | `[docs] update README` |
| `style` | Code formatting (no logic change) | `[style] clean up code style` |
| `refactor` | Code refactoring | `[refactor] improve auth module structure` |
| `test` | Test code addition | `[test] add unit tests` |
| `chore` | Build/config changes | `[chore] update dependencies` |
| `design` | UI/UX design changes | `[design] improve button styling` |
| `comment` | Comment addition/changes | `[comment] add API function comments` |
| `rename` | File/folder rename | `[rename] rename component files` |
| `remove` | File deletion | `[remove] remove unused files` |
| `!BREAKING CHANGE` | Major API changes | `[!BREAKING CHANGE] migrate to API v2` |
| `!HOTFIX` | Critical bug fixes | `[!HOTFIX] urgent security vulnerability fix` |

### Section-specific Guide

#### Body Section (Optional)
```
[Body]
- Authentication system implementation complete
- JWT token-based session management
- Password encryption added
- Login failure retry limitation
```

#### Todo Section (Optional)
```
[Todo]
@authentication
- Add social login integration
- Implement password recovery feature
- Introduce 2FA authentication system

@testing
- Write authentication flow unit tests
- Add security vulnerability tests
```

#### Footer Section (Optional)
```
[Footer]
Closes #123, #124
Related to #125
Breaking Change: API v1 is no longer supported
Co-authored-by: Developer Name <email@example.com>
```

### Commit Message Examples

#### Basic Commit
```
[feat] implement user dashboard
```

#### Commit with Scope  
```
[fix(auth)] resolve login session expiry bug
```

#### Complete Structure Commit
```
[feat] implement real-time notification system

[Body]
- WebSocket-based real-time communication implementation
- Notification type classification system added
- User-specific notification settings management feature
- Notification history storage and retrieval

[Todo]
@notification
- Add push notification integration
- Improve email notification templates
- Implement notification statistics dashboard

@performance  
- Optimize notification queue
- Performance testing for high-volume users

[Footer]
Closes #456
Related to #457, #458
```

### Commit Message Validation

The system automatically validates:
- ✅ [type] format compliance
- ✅ Supported commit type usage
- ✅ Correct section structure
- ✅ Todo category format (@category)
- ✅ Footer issue reference format

## 🎯 Workflows

### Automatic Triggers
- **Push to main/master/develop**: DSR generation and project synchronization
- **Issues changes**: Automatic project board updates
- **Project board changes**: Automatic issue label synchronization
- **Manual execution**: Manual triggers available in GitHub Actions

### Execution Modes
```bash
# Workflow tracking (DSR generation)
python main.py --mode workflow

# Task management (project synchronization) 
python main.py --mode task-management

# Project report generation
python main.py --mode report

# System health check
python main.py --health-check

# Dry run (test without changes)
python main.py --dry-run --verbose
```

## 🔍 Monitoring and Validation

### System Health Check
```bash
# Complete system validation
python validate_implementation.py

# Individual component check
python main.py --health-check
```

### Log Review
System logs are output at the following levels:
- `DEBUG`: Detailed execution information
- `INFO`: General execution status  
- `WARNING`: Situations requiring attention
- `ERROR`: Error situations

## 🛠 Advanced Configuration

### Custom Field Mapping
```yaml
project_sync:
  custom_fields:
    "Estimate": "estimate_field_id"
    "Sprint": "sprint_field_id"
```

### Notification Settings (Optional)
```yaml
notifications:
  slack:
    enabled: false
    webhook_url: "${SLACK_WEBHOOK_URL}"
  
  email:
    enabled: false
    recipients: ["team@example.com"]
```

### Performance Optimization
```yaml
performance:
  batch_size: 50              # Batch processing size
  concurrent_requests: 5      # Concurrent request count
  cache_duration: 300         # Cache duration (seconds)
```

## 📊 Metrics and Analytics

The system automatically collects the following metrics:
- API call success/failure rates
- Processing time statistics  
- Project completion rates
- DSR generation statistics
- Error occurrence frequency

## 🤝 Contributing

To contribute to system improvements:
1. Bug reports or feature suggestions in Issues tab
2. Code contributions through Pull Requests
3. Documentation improvement suggestions

## 📄 License

This project is a configuration template for personal/team use. Feel free to use and modify.

---

<div align="center">

### 🔗 Related Links

[Main Settings Repository](../../) • 
[TaskManagement](../TaskManagement/) •
[BaekjoonLogging](../BaekjoonLogging/)

**🚀 Experience more efficient development workflows with GitHub Automation!**

</div>
# GitHub Personal Access Token (PAT) Setup

## Why PAT is Required

The GitHub automation system requires a **Personal Access Token (PAT)** with specific scopes to create and manage GitHub Projects v2 boards. The default `GITHUB_TOKEN` provided by GitHub Actions has limited permissions and **cannot create Projects v2**.

## Error Symptoms

If you see these errors in your GitHub Actions logs:
```
⚠️  GITHUB ACTIONS TOKEN LIMITATION DETECTED
GitHub Actions tokens have limited permissions for Projects v2 operations
```

Or:
```
Failed to create project '.Settings' for Anxi77
Could not resolve to an Organization with the login of 'Anxi77'
```

This indicates you need to set up a PAT token.

## PAT Setup Instructions

### 1. Create Personal Access Token

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens/new)
2. Select **"Generate new token (classic)"** 
3. Set a descriptive name: `GitHub Automation - [Your Repo Name]`
4. Choose expiration (recommend 90 days or 1 year)
5. **Select these scopes:**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `project` (Full control of projects) - **CRITICAL for Projects v2**
   - ✅ `write:org` (Write org and team membership) - if using organization projects

### 2. Add PAT to Repository Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `PAT`
5. Value: Paste your PAT token (starts with `ghp_` or `github_pat_`)
6. Click **"Add secret"**

### 3. Workflow Configuration

The GitHub Actions workflow is already configured to use your PAT automatically:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.PAT || secrets.GITHUB_TOKEN }}
```

This means:
- If `PAT` secret exists → Uses PAT (full permissions)
- If `PAT` secret missing → Falls back to `GITHUB_TOKEN` (limited permissions)

## Testing the Setup

After adding your PAT secret:

1. Push a commit with TODO items to test:
```bash
git add .
git commit -m "[test] Verify PAT token project creation

[Todo]
@testing  
- Verify project auto-creation works with PAT token
"
git push
```

2. Check the GitHub Actions logs for:
```
Initializing API client with Personal Access Token
Created user project '.Settings' (#1)
```

## Troubleshooting

### PAT Token Not Working
- Verify the token has `project` scope checked
- Ensure token hasn't expired  
- Check that your GitHub account has Projects enabled
- Try regenerating the token if it's old

### Organization vs User Projects
- Personal repositories → Uses User projects
- Organization repositories → Tries User first, then Organization projects
- Organization projects require `write:org` scope in addition to `project`

### Still Getting Errors?
Check the detailed error logs in GitHub Actions for specific permission issues or contact your organization admin if using organization repositories.

## Security Notes

- Never commit PAT tokens to your repository
- Use repository secrets to store the PAT securely
- Set reasonable expiration dates on PAT tokens  
- Regularly rotate PAT tokens for security
- Only grant minimum required scopes

## Alternative: GitHub Apps

For organizations, consider using GitHub Apps instead of PAT tokens for better security and fine-grained permissions. However, PAT tokens are simpler for personal repositories and small teams.
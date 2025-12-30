# Scripts

This directory contains utility scripts for maintaining the DeltaPag GitHub profile.

## update_readme.py

Updates the profile README with current repository information, automatically categorizing repositories into:
- **In Production**: Active production repositories
- **In Development**: Work-in-progress repositories
- **Templates**: Repository templates
- **Deprecated**: Deprecated repositories

### Usage

#### Prerequisites

Install required dependencies:

```bash
pip install -r requirements.txt
```

#### Running the Script

1. **Set GitHub Token** (required for API access):
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```

2. **Run the script**:
   ```bash
   python scripts/update_readme.py [org_name] [token]
   ```

   - `org_name`: GitHub organization or username (default: `deltapag`)
   - `token`: GitHub personal access token (optional if GITHUB_TOKEN env var is set)

### Repository Categorization

Repositories are automatically categorized based on:

- **Templates**: Repository is marked as a template, or name/topics contain "template"
- **Deprecated**: Name, topics, or description contain "deprecated"
- **In Development**: Name contains "wip", "dev", "development" or topics contain "wip", "work-in-progress", "in-dev", "development"
- **In Production**: All other repositories

### Manual Categorization

To manually categorize repositories, you can:

1. Add GitHub topics to repositories:
   - `template` - for template repositories
   - `deprecated` - for deprecated repositories
   - `wip`, `work-in-progress`, `in-dev`, `development` - for repositories in development

2. Include keywords in repository names or descriptions

### GitHub Actions

The README is automatically updated daily via GitHub Actions workflow (`.github/workflows/update-readme.yml`). The workflow runs:
- Daily at 00:00 UTC
- On manual trigger (workflow_dispatch)
- When the workflow file is updated


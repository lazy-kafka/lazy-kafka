# Scripts Directory

This directory contains utility scripts for managing the lazy-kafka project, including roadmap, milestone, issue creation, and CI/CD helper scripts.

---

## 📋 Available Scripts

| Script | Purpose | Requirements | Usage |
|--------|---------|--------------|-------|
| `create_github_resources.py` | Create milestones and issues via GitHub CLI | Python 3.11+, GitHub CLI (gh) | `python create_github_resources.py --all` |
| `create-milestones.sh` | Create milestones via GitHub CLI (bash) | bash, GitHub CLI (gh) | `./create-milestones.sh` |
| `create-milestones-curl.sh` | Create milestones via GitHub API (curl) | bash, curl, jq | `./create-milestones-curl.sh --token YOUR_TOKEN` |

---

## 🚀 Quick Start

### Option 1: Using GitHub CLI (Recommended)

```bash
# Install GitHub CLI if not already installed
# Ubuntu/Debian: sudo apt-get install gh
# macOS: brew install gh
# Windows: winget install --id GitHub.cli

# Authenticate
gh auth login

# Create all milestones and sample issues (dry run first)
python create_github_resources.py --dry-run --all

# Actually create them
python create_github_resources.py --all
```

### Option 2: Using curl (No GitHub CLI needed)

```bash
# Install curl and jq if not already installed
# Ubuntu/Debian: sudo apt-get install curl jq
# macOS: brew install curl jq

# Create a GitHub Personal Access Token:
# 1. Go to https://github.com/settings/tokens
# 2. Create a new token with 'repo' scope
# 3. Copy the token

# Create milestones (dry run first)
./create-milestones-curl.sh --dry-run --token YOUR_TOKEN

# Actually create them
./create-milestones-curl.sh --token YOUR_TOKEN
```

---

## 📦 Script Details

### create_github_resources.py

**Purpose**: Create GitHub milestones and issues using GitHub CLI

**Features**:
- Creates all 9 milestones from the roadmap
- Creates sample issues for each milestone
- Supports dry-run mode
- Updates existing milestones instead of duplicating
- Uses Python dataclasses for clean milestone/issue definitions

**Usage**:
```bash
# Show help
python create_github_resources.py --help

# Create all milestones and issues
python create_github_resources.py --all

# Create only milestones
python create_github_resources.py --create-milestones

# Create only issues
python create_github_resources.py --create-issues

# Dry run mode (preview what will be created)
python create_github_resources.py --dry-run --all

# Specify a different repository
python create_github_resources.py --repo owner/repo --all
```

**Requirements**:
- Python 3.11+
- GitHub CLI (gh) installed and authenticated
- bash (for subprocess calls)

**Milestones Created**:
- v0.1.1 (2026-09-13) - Phase 1: Test Infrastructure & Critical Bug Fixes
- v0.1.2 (2026-09-20) - Phase 1: Plugin System Tests & Integration
- v0.1.3 (2026-09-27) - Phase 1: Error Handling & Logging Improvements
- v0.2.0 (2026-10-25) - Phase 2: Complete Message Streaming
- v0.2.1 (2026-11-01) - Phase 3: Settings & Configuration
- v0.2.2 (2026-11-08) - Phase 3: UX Improvements
- v0.2.3 (2026-11-15) - Phase 3: Schema Registry Enhancements
- v0.3.0 (2026-12-13) - Phase 4: Advanced Features
- v1.0.0 (2027-02-07) - Phase 5: REST API Migration & Code Generation

**Issues Created**:
- Sample issues for v0.1.1, v0.1.2, and v0.2.0 milestones
- Includes proper labels (bug, test, enhancement, documentation, priority:high/medium)

---

### create-milestones.sh

**Purpose**: Create GitHub milestones using GitHub CLI (bash version)

**Usage**:
```bash
# Dry run
./create-milestones.sh --dry-run

# Create milestones
./create-milestones.sh
```

**Requirements**:
- bash
- GitHub CLI (gh) installed and authenticated

**Features**:
- Simple bash script
- Creates all 9 milestones
- Dry-run mode available
- Updates existing milestones

---

### create-milestones-curl.sh

**Purpose**: Create GitHub milestones using GitHub REST API via curl

**Usage**:
```bash
# Dry run
./create-milestones-curl.sh --dry-run --token YOUR_TOKEN

# Create milestones
./create-milestones-curl.sh --token YOUR_TOKEN

# Using environment variable
GITHUB_TOKEN=your_token_here ./create-milestones-curl.sh
```

**Requirements**:
- bash
- curl
- jq
- GitHub Personal Access Token with 'repo' scope

**Features**:
- Uses GitHub REST API directly
- No GitHub CLI required
- Dry-run mode available
- Checks for existing milestones before creating
- Updates existing milestones

---

## 🎯 Post-Creation Steps

After creating milestones, you should:

### 1. Verify Milestones

```bash
# Using GitHub CLI
gh issue list --milestone v0.1.1

# Using curl
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.github.com/repos/Timon Viola/lazy-kafka/milestones" | jq '.[] | {title, number, due_on}'
```

### 2. Create Additional Issues

The scripts create sample issues, but you'll want to create issues for all tasks in ROADMAP.md:

```bash
# Create an issue and link to milestone
gh issue create \
  --title "Fix consumer poll errors" \
  --body "Description of the issue" \
  --milestone v0.1.1 \
  --label bug,priority:high,kafka
```

### 3. Create Labels

Create the recommended labels if they don't exist:

```bash
# Single label
gh label create "enhancement" --color "006b75" --description "New features"

# Multiple labels
for label in "bug:d73a4a" "documentation:0075ca" "test:1d76db"; do
  IFS=':' read -r name color <<< "$label"
  gh label create "$name" --color "$color"
done
```

Recommended labels:
- `enhancement` (006b75) - New features
- `bug` (d73a4a) - Bug fixes
- `documentation` (0075ca) - Documentation
- `test` (1d76db) - Testing
- `priority:high` (d93f0b) - High priority
- `priority:medium` (fbca04) - Medium priority
- `priority:low` (0e8a16) - Low priority
- `kafka` (005cc5) - Kafka-related
- `connect` (005cc5) - Kafka Connect
- `registry` (005cc5) - Schema Registry
- `tui` (795548) - Textual TUI
- `cli` (795548) - Command-line interface

---

## 📊 JSON Data File

**File**: `github_api_create_milestones.json`

**Purpose**: Contains all milestone definitions in JSON format for use with curl or other API clients

**Structure**:
```json
{
  "milestones": [
    {
      "title": "v0.1.1",
      "description": "...",
      "due_on": "2026-09-13T23:59:59Z",
      "state": "open"
    },
    ...
  ]
}
```

You can use this file directly with curl:

```bash
# Create a single milestone using the JSON file
milestone=$(jq '.milestones[0]' github_api_create_milestones.json)
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d "$milestone" \
  "https://api.github.com/repos/Timon Viola/lazy-kafka/milestones"
```

---

## 🛠️ Troubleshooting

### GitHub CLI Authentication

```bash
# Check if authenticated
gh auth status

# Re-authenticate
gh auth login

# Check token
gh auth status --show-token
```

### Token Issues

If you get authentication errors:

1. **Token expired**: Create a new token at https://github.com/settings/tokens
2. **Insufficient scope**: Ensure your token has 'repo' scope
3. **Token not found**: Make sure to export it or pass via --token

### Rate Limiting

GitHub API has rate limits:
- Authenticated: 5,000 requests per hour
- Unauthenticated: 60 requests per hour

If you hit rate limits, wait an hour or use authentication.

### Network Issues

```bash
# Test connectivity to GitHub API
curl -I https://api.github.com

# Test authentication
curl -I -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/user
```

---

## 📚 Related Documentation

- [ROADMAP.md](../ROADMAP.md) - Project roadmap
- [.github/ROADMAP_SETUP.md](../.github/ROADMAP_SETUP.md) - Setup guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [TESTING.md](../TESTING.md) - Testing guidelines

---

## 🎨 Script Development

### Adding a New Milestone

1. Edit `create_github_resources.py`
2. Add a new `Milestone` object to the `MILESTONES` list
3. Add issues for the milestone to the `ISSUES` dict
4. Update `create-milestones.sh` and `create-milestones-curl.sh`

### Testing Scripts

```bash
# Test Python script in dry-run mode
python create_github_resources.py --dry-run --all

# Test bash script in dry-run mode
./create-milestones.sh --dry-run
./create-milestones-curl.sh --dry-run --token test_token
```

---

*Last updated: 2026-08-30*

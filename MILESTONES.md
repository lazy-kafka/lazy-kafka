# Lazy-Kafka Milestones

> **Current Date**: 2026-09-12 | **Roadmap Version**: 1.0 | **Total Milestones**: 9

This document provides a quick overview of all milestones for the lazy-kafka project. For detailed information, see [ROADMAP.md](ROADMAP.md).

---

## 🎯 Overview

| Milestone | Due Date | Phase | Focus | Status |
|----------|----------|-------|-------|--------|
| `v0.1.1` | 2026-09-19 | Phase 1 | Test Infrastructure & Critical Bug Fixes | 🟡 In Progress |
| `v0.1.2` | 2026-09-26 | Phase 1 | Plugin System Tests & Integration | 📋 Planned |
| `v0.1.3` | 2026-10-03 | Phase 1 | Error Handling & Logging | 📋 Planned |
| `v0.2.0` | 2026-10-31 | Phase 2 | Complete Message Streaming | 📋 Planned |
| `v0.2.1` | 2026-11-07 | Phase 3 | Settings & Configuration | 📋 Planned |
| `v0.2.2` | 2026-11-14 | Phase 3 | UX Improvements | 📋 Planned |
| `v0.2.3` | 2026-11-21 | Phase 3 | Schema Registry Enhancements | 📋 Planned |
| `v0.3.0` | 2026-12-19 | Phase 4 | Advanced Features | 📋 Planned |
| `v1.0.0` | 2027-02-13 | Phase 5 | REST API Migration & Code Generation | 📋 Planned |

**Total Duration**: ~22 weeks (5.5 months)

---

## 📊 Phases Breakdown

### Phase 1: Stability & Testing (3 weeks)
**Goal**: Establish a solid foundation with comprehensive testing, bug fixes, and error handling.

- **v0.1.1** (1 week): Critical bug fixes, test infrastructure, documentation
- **v0.1.2** (1 week): Plugin system tests, integration, CLI tests
- **v0.1.3** (1 week): Error handling, logging improvements

**Target Coverage**: 80%

---

### Phase 2: Message Streaming (4 weeks)
**Goal**: Complete message consumption and production features with TUI and CLI support.

- **v0.2.0** (4 weeks): Message table widget, real-time streaming, CLI enhancements

**Target Coverage**: 85%

---

### Phase 3: Enhancements (3 weeks)
**Goal**: Improve user experience, configuration management, and schema registry features.

- **v0.2.1** (1 week): Settings screen, file watcher, configuration profiles
- **v0.2.2** (1 week): UX improvements, keyboard shortcuts, accessibility
- **v0.2.3** (1 week): Schema browsing, creation, validation, CLI enhancements

**Target Coverage**: 85%

---

### Phase 4: Advanced Features (4 weeks)
**Goal**: Add production-ready features including multi-broker support, authentication, and monitoring.

- **v0.3.0** (4 weeks): Multi-broker, auth, filtering, monitoring, performance

**Target Coverage**: 88%

---

### Phase 5: Architecture Migration (8 weeks)
**Goal**: Migrate to Kafka REST API, add code generation, and prepare for v1.0 release.

- **v1.0.0** (8 weeks): REST API integration, plugin extensibility, code generation

**Target Coverage**: 90%

---

## 📅 Timeline

```
September 2026:
  Week 1 (Sep 12-19): v0.1.1 - Test Infrastructure & Bug Fixes ✅
  Week 2 (Sep 19-26): v0.1.2 - Plugin System Tests
  Week 3 (Sep 26-Oct 3): v0.1.3 - Error Handling & Logging

October 2026:
  Week 4-7 (Oct 3-31): v0.2.0 - Message Streaming

November 2026:
  Week 8 (Oct 31-Nov 7): v0.2.1 - Settings & Configuration
  Week 9 (Nov 7-14): v0.2.2 - UX Improvements
  Week 10 (Nov 14-21): v0.2.3 - Schema Registry Enhancements

December 2026:
  Week 11-14 (Nov 21-Dec 19): v0.3.0 - Advanced Features

January-February 2027:
  Week 15-22 (Dec 19-Feb 13): v1.0.0 - REST API Migration
```

---

## 🎯 Key Deliverables by Milestone

### v0.1.1 (2026-09-19)
- ✅ All critical bugs fixed
- ✅ Unit tests for core modules (topic.py, config.py, registry.py, connect.py)
- ✅ pytest infrastructure with fixtures
- ✅ CONTRIBUTING.md and TESTING.md
- ✅ GitHub Actions workflow for tests
- ✅ Test coverage: 70%

### v0.1.2 (2026-09-26)
- ✅ Plugin system fully tested
- ✅ Integration tests for CLI and TUI
- ✅ Plugin development documentation
- ✅ Test coverage: 75%

### v0.1.3 (2026-10-03)
- ✅ Consistent error handling across all modules
- ✅ Structured logging with JSON format
- ✅ CLI log level configuration
- ✅ Connection retry with exponential backoff
- ✅ Test coverage: 80%

### v0.2.0 (2026-10-31)
- ✅ Real-time message streaming in TUI
- ✅ Message table widget with filtering and search
- ✅ CLI consume/produce commands with options
- ✅ Pretty-print JSON messages
- ✅ Test coverage: 85%

### v0.2.1 (2026-11-07)
- ✅ Editable settings in TUI
- ✅ Config file watcher
- ✅ Multiple configuration profiles
- ✅ Environment variable support

### v0.2.2 (2026-11-14)
- ✅ Keyboard shortcuts cheat sheet
- ✅ Command palette
- ✅ Theme customization
- ✅ Message detail view and export
- ✅ Accessibility improvements

### v0.2.3 (2026-11-21)
- ✅ Schema version selection and diff
- ✅ Schema validation
- ✅ Schema editor
- ✅ CLI enhancements for schema operations

### v0.3.0 (2026-12-19)
- ✅ Multi-broker support
- ✅ SASL/SCRAM and SSL/TLS authentication
- ✅ Message filtering by headers
- ✅ Kafka Connect connector management
- ✅ Performance optimizations
- ✅ Metrics dashboard

### v1.0.0 (2027-02-13)
- ✅ Kafka REST API client (generated from OpenAPI)
- ✅ Replace confluent-kafka with REST API
- ✅ Plugin system extensibility
- ✅ Code generation (Python, TypeScript)
- ✅ Migration guide from v0.x
- ✅ Test coverage: 90%

---

## 🚀 Creating GitHub Milestones

To create all milestones on GitHub:

### Using Python Script (Recommended)

```bash
# Dry run first
python scripts/create_github_resources.py --dry-run --all

# Create all milestones and sample issues
python scripts/create_github_resources.py --all

# Create only milestones
python scripts/create_github_resources.py --create-milestones

# Create only issues
python scripts/create_github_resources.py --create-issues
```

**Prerequisites**:
- [GitHub CLI (gh)](https://cli.github.com/) installed
- Authenticated with `gh auth login`
- Python 3.11+

### Using Bash Script

```bash
# Dry run
./scripts/create-milestones.sh --dry-run

# Create milestones
./scripts/create-milestones.sh
```

---

## 📊 Test Coverage Goals

| Milestone | Total Coverage | Key Modules |
|----------|---------------|-------------|
| v0.1.1 | 70% | Core modules at 70-90% |
| v0.1.2 | 75% | Plugin system at 90% |
| v0.1.3 | 80% | All modules at 80%+ |
| v0.2.0 | 85% | Message streaming fully covered |
| v0.2.1-0.2.3 | 85% | Configuration and UX features |
| v0.3.0 | 88% | Advanced features covered |
| v1.0.0 | 90% | Full coverage |

---

## 📚 Documentation Deliverables

| Document | First Version | Major Update |
|----------|---------------|--------------|
| README.md | Already exists | v0.2.0, v1.0.0 |
| CONTRIBUTING.md | v0.1.1 | v0.2.0 |
| TESTING.md | v0.1.1 | v0.2.0 |
| Configuration Guide | v0.2.1 | v0.3.0 |
| User Guide | v0.2.0 | v0.2.3 |
| Plugin Development Guide | v0.2.3 | v1.0.0 |
| CLI Reference | v0.2.0 | v0.3.0 |
| API Reference | - | v1.0.0 |
| Migration Guide | - | v1.0.0 |

---

## 🎨 Labels

### Priority Labels
- `priority:high` - Must have for next release
- `priority:medium` - Important, but can wait
- `priority:low` - Nice to have

### Component Labels
- `kafka` - Kafka-related tasks
- `connect` - Kafka Connect-related tasks
- `registry` - Schema Registry-related tasks
- `tui` - Textual TUI tasks
- `cli` - Command-line interface tasks

### Type Labels
- `enhancement` - New features
- `bug` - Bug fixes
- `documentation` - Documentation tasks
- `test` - Testing tasks

---

## 📞 Quick Commands

```bash
# List all milestones
gh issue list --milestone v0.1.1

# View milestone progress
gh api repos/Timon\ Viola/lazy-kafka/milestones --jq '.[] | select(.title == "v0.1.1")'

# Create an issue for a milestone
gh issue create --title "Fix consumer poll errors" \
  --body "Description" \
  --milestone v0.1.1 \
  --label bug,priority:high,kafka

# List issues for a milestone
gh issue list --milestone v0.1.1 --state all

# Check CI/CD status
gh run list --workflow build.yaml
```

---

## 🔗 Related Documents

- [ROADMAP.md](ROADMAP.md) - Detailed roadmap with all features and tasks
- [.github/ROADMAP_SETUP.md](.github/ROADMAP_SETUP.md) - Setup guide for roadmap and CI/CD
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [TESTING.md](TESTING.md) - Testing guidelines

---

*Generated: 2026-09-12*
*Maintainer: @timonviola*

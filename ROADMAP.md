# Lazy-Kafka Roadmap

> **Status**: Active Development | **Current Version**: 0.1.0 | **Target**: 1.0.0 | **Last Updated**: 2026-09-12

This document outlines the development roadmap for lazy-kafka, a TUI/CLI application for Kafka ecosystem development experience.

---

## 🗺️ Overview

| Phase | Version Range | Duration | Focus Area | Status |
|-------|---------------|----------|------------|--------|
| **Phase 1** | v0.1.1 - v0.1.3 | ~3 weeks | Stability & Testing | 🟡 In Progress |
| **Phase 2** | v0.2.0 | ~4 weeks | Message Streaming | 📋 Planned |
| **Phase 3** | v0.2.1 - v0.2.3 | ~3 weeks | UX & Configuration | 📋 Planned |
| **Phase 4** | v0.3.0 | ~4 weeks | Advanced Features | 📋 Planned |
| **Phase 5** | v1.0.0 | ~8 weeks | REST API Migration | 📋 Planned |

**Total Estimated Duration**: ~22 weeks (5.5 months)

---

## 🎯 Phase 1: Stability & Testing (v0.1.1 - v0.1.3)

**Goal**: Establish a solid foundation with comprehensive testing, bug fixes, and error handling.

### v0.1.1 - Critical Bug Fixes & Test Infrastructure
**Duration**: 1 week | **Milestone**: `v0.1.1` | **Due**: 2026-09-19

#### 🐛 Bug Fixes
- [ ] Fix consumer poll errors and edge cases
- [ ] Fix offset invalid error handling
- [ ] Fix message serialization edge cases (None, empty, malformed JSON)
- [ ] Add proper error messages for connection failures
- [ ] Add connection retry logic with exponential backoff

#### 🧪 Testing
- [ ] Unit tests for `topic.py` (KafkaClient, message handling)
- [ ] Unit tests for `config.py` (configuration loading)
- [ ] Unit tests for `registry.py` (SchemaRegistry operations)
- [ ] Unit tests for `connect.py` (Connect operations)
- [ ] Set up pytest fixtures (mock clients, HTTP responses, temp configs)
- [ ] Configure pytest-cov for coverage reporting
- [ ] Add GitHub Actions workflow for test execution

#### 📚 Documentation
- [ ] Add `CONTRIBUTING.md` with development setup, testing guidelines, PR template
- [ ] Add `TESTING.md` with test structure, how to run/add tests
- [ ] Update README with current features and limitations

#### ✅ Success Criteria
- Test coverage: **70%**
- All critical bugs fixed
- ruff and mypy passing

---

### v0.1.2 - Plugin System Tests & Integration
**Duration**: 1 week | **Milestone**: `v0.1.2`

#### ✅ Features
- [ ] Fix plugin registration edge cases
- [ ] Add plugin loading error handling
- [ ] Add structured logging (JSON format option)

#### 🧪 Testing (Priority: P0)
- [ ] Unit tests for `plugin/__init__.py` (register, iter_plugins, load_builtin_plugins)
- [ ] Unit tests for each plugin module
- [ ] Integration tests for plugin CLI commands
- [ ] Integration tests for TUI panel mounting
- [ ] CLI tests for `cli/_cli.py` (global options, version callback, config loading)

#### 📚 Documentation
- [ ] Add plugin development guide to CONTRIBUTING.md
- [ ] Document plugin architecture

#### 🎯 Success Criteria
- Test coverage: **75%**
- Plugin system fully tested

---

### v0.1.3 - Error Handling & Logging Improvements
**Duration**: 1 week | **Milestone**: `v0.1.3` | **Due**: 2026-10-03

#### ✅ Features
- [ ] Add consistent error handling across all modules
- [ ] Add structured logging (JSON format option)
- [ ] Add log level configuration via CLI
- [ ] Add connection retry logic with exponential backoff

#### 🧪 Testing
- [ ] Add tests for error scenarios
- [ ] Add tests for logging configuration
- [ ] Integration test: Verify error messages are user-friendly

#### 📚 Documentation
- [ ] Add error handling documentation
- [ ] Add logging configuration guide

#### ✅ Success Criteria
- Test coverage: **80%**
- Consistent error handling across all modules

---

## 🚀 Phase 2: Message Streaming (v0.2.0)

**Goal**: Complete message consumption and production features with TUI and CLI support.

### v0.2.0 - Complete Message Streaming
**Duration**: 4 weeks | **Milestone**: `v0.2.0` | **Due**: 2026-10-31

#### ✅ Features (Priority: P1)
- [ ] **Consume Messages in TUI**
  - [ ] Add message table widget to TopicPanel
  - [ ] Add real-time message streaming with auto-refresh
  - [ ] Add message filtering (by key, timestamp range)
  - [ ] Add message search functionality
  - [ ] Add pause/resume streaming
  - [ ] Handle large message payloads (truncation, expandable)
  
- [ ] **Produce Messages in TUI**
  - [ ] Add produce dialog/modal screen
  - [ ] Support manual message entry
  - [ ] Support template-based message generation
  - [ ] Add produce confirmation and status

- [ ] **CLI Improvements**
  - [ ] `kafka consume` - Add `--max-messages`, `--timeout`, `--output-format` (json, raw)
  - [ ] `kafka produce` - Add `--count`, `--interval`, `--template` options
  - [ ] Add `kafka topics` command to list topics
  - [ ] Add `kafka topic info <name>` command for topic details

- [ ] **Message Display**
  - [ ] Pretty-print JSON messages
  - [ ] Syntax highlighting for JSON
  - [ ] Timestamp formatting options
  - [ ] Message size display

#### 🧪 Testing
- [ ] Unit tests for message consumption logic
- [ ] Unit tests for message production logic
- [ ] Integration tests for CLI consume/produce commands
- [ ] Integration tests for TUI message display
- [ ] Performance tests for large message volumes

#### 📚 Documentation
- [ ] Add user guide for message consumption
- [ ] Add user guide for message production
- [ ] Add CLI reference documentation

#### 🎯 Success Criteria
- Complete message streaming functionality
- Test coverage: **85%**
- CLI and TUI parity for message operations

---

## ✨ Phase 3: Enhancements (v0.2.1 - v0.2.3)

**Goal**: Improve user experience, configuration management, and schema registry features.

### v0.2.1 - Settings & Configuration
**Duration**: 1 week | **Milestone**: `v0.2.1` | **Due**: 2026-11-07

#### ✅ Features
- [ ] **Settings Screen**: Make settings editable in TUI
- [ ] **File Watcher**: Implement config file watching (using watchdog)
- [ ] **Configuration Enhancements**
  - [ ] Support multiple configuration profiles
  - [ ] Add environment variable support
  - [ ] Add command-line overrides for all config options

#### 🧪 Testing
- [ ] Unit tests for settings screen
- [ ] Unit tests for file watcher
- [ ] Integration tests for config loading from various sources

#### 📚 Documentation
- [ ] Add configuration reference
- [ ] Add examples for different configuration scenarios

---

### v0.2.2 - UX Improvements
**Duration**: 1 week | **Milestone**: `v0.2.2` | **Due**: 2026-11-14

#### ✅ Features
- [ ] **TUI Enhancements**
  - [ ] Add keyboard shortcuts cheat sheet
  - [ ] Add command palette
  - [ ] Add theme customization
  - [ ] Improve tab navigation
  - [ ] Add breadcrumb navigation for nested views
- [ ] **Message Display**
  - [ ] Add message detail view (modal)
  - [ ] Add message comparison (diff view)
  - [ ] Add message export (copy to clipboard, save to file)
- [ ] **Accessibility**
  - [ ] Add screen reader support
  - [ ] Improve color contrast

#### 🧪 Testing
- [ ] Manual testing for UX flows
- [ ] Accessibility testing

#### 📚 Documentation
- [ ] Add keyboard shortcuts reference
- [ ] Add theme customization guide

---

### v0.2.3 - Schema Registry Enhancements
**Duration**: 1 week | **Milestone**: `v0.2.3` | **Due**: 2026-11-21

#### ✅ Features
- [ ] **Schema Browsing**
  - [ ] Add schema version selection
  - [ ] Add schema diff between versions
  - [ ] Add schema validation
- [ ] **Schema Creation**
  - [ ] Add schema editor (modal)
  - [ ] Add schema validation before creation
  - [ ] Add schema import from file
- [ ] **CLI Enhancements**
  - [ ] `schema-registry get <subject> [--version]`
  - [ ] `schema-registry validate <subject> <schema>`
  - [ ] `schema-registry diff <subject> <version1> <version2>`

#### 🧪 Testing
- [ ] Unit tests for schema operations
- [ ] Integration tests for schema CLI commands

#### 📚 Documentation
- [ ] Add schema registry user guide

---

## 🔧 Phase 4: Advanced Features (v0.3.0)

**Goal**: Add production-ready features including multi-broker support, authentication, and monitoring.

### v0.3.0 - Production-Ready Features
**Duration**: 4 weeks | **Milestone**: `v0.3.0` | **Due**: 2026-12-19

#### ✅ Features (Priority: P2)
- [ ] **Multi-Broker Support**
  - [ ] Add multiple Kafka cluster configurations
  - [ ] Add cluster switching in TUI
  - [ ] Add cluster health monitoring
- [ ] **Authentication & Security**
  - [ ] Add SASL/SCRAM authentication
  - [ ] Add SSL/TLS support
  - [ ] Add credential management (encrypted storage)
  - [ ] Add certificate validation
- [ ] **Message Filtering & Processing**
  - [ ] Add message filtering by headers
  - [ ] Add message transformation (pretty-print, extract fields)
  - [ ] Add message statistics (count, rate, size)
- [ ] **Kafka Connect Enhancements**
  - [ ] Add connector creation UI
  - [ ] Add connector configuration editing
  - [ ] Add connector restart/pause/resume
  - [ ] Add connector logs viewing
- [ ] **Performance**
  - [ ] Add async message consumption
  - [ ] Add message batching for production
  - [ ] Add connection pooling
- [ ] **Monitoring**
  - [ ] Add metrics dashboard (topic size, message rate, etc.)
  - [ ] Add health checks
  - [ ] Add alerting (basic)

#### 🧪 Testing
- [ ] Unit tests for authentication
- [ ] Integration tests for multi-broker scenarios
- [ ] Performance tests
- [ ] Security tests

#### 📚 Documentation
- [ ] Add security configuration guide
- [ ] Add multi-cluster setup guide
- [ ] Add performance tuning guide

#### 🎯 Success Criteria
- Test coverage: **88%**
- All production features implemented

---

## 🏗️ Phase 5: Architecture Migration (v1.0.0)

**Goal**: Migrate to Kafka REST API, add code generation, and prepare for v1.0 release.

### v1.0.0 - REST API & Code Generation
**Duration**: 8 weeks | **Milestone**: `v1.0.0` | **Due**: 2027-02-13

#### ✅ Architecture Changes
- [ ] **Kafka REST API Integration**
  - [ ] Generate client code from OpenAPI spec
  - [ ] Implement Kafka REST API client
  - [ ] Replace confluent-kafka with REST API for all operations
  - [ ] Add fallback to confluent-kafka for unsupported operations
- [ ] **Plugin System Enhancements**
  - [ ] Make plugin system extensible via entry points
  - [ ] Add plugin discovery from external packages
  - [ ] Add plugin configuration
- [ ] **Code Generation**
  - [ ] Generate Python client from OpenAPI specs
  - [ ] Generate TypeScript client (optional)
  - [ ] Generate documentation from schemas

#### ✅ Features
- [ ] **New CLI Commands**: REST API-based commands
- [ ] **TUI Improvements**: REST API-based panels
- [ ] **Enhanced Error Handling**: Improved REST API error handling

#### 🧪 Testing
- [ ] Comprehensive integration tests for REST API
- [ ] Comparison tests (REST vs confluent-kafka)
- [ ] Performance comparison

#### 📚 Documentation
- [ ] Migration guide from v0.x to v1.0
- [ ] REST API reference
- [ ] Plugin development guide (external plugins)

#### 🎯 Success Criteria
- Test coverage: **90%**
- Full REST API support
- Migration guide complete

---

## 📅 Release Schedule

| Version | Target Date | Milestone | Status | Notes |
|---------|-------------|----------|--------|-------|
| v0.1.1 | 2026-09-19 | `v0.1.1` | 🟡 In Progress | Test infrastructure, bug fixes |
| v0.1.2 | 2026-09-26 | `v0.1.2` | 📋 Planned | Plugin tests, integration |
| v0.1.3 | 2026-10-03 | `v0.1.3` | 📋 Planned | Error handling, logging |
| v0.2.0 | 2026-10-31 | `v0.2.0` | 📋 Planned | Message streaming |
| v0.2.1 | 2026-11-07 | `v0.2.1` | 📋 Planned | Settings, file watcher |
| v0.2.2 | 2026-11-14 | `v0.2.2` | 📋 Planned | UX improvements |
| v0.2.3 | 2026-11-21 | `v0.2.3` | 📋 Planned | Schema registry enhancements |
| v0.3.0 | 2026-12-19 | `v0.3.0` | 📋 Planned | Advanced features |
| v1.0.0 | 2027-02-13 | `v1.0.0` | 📋 Planned | Architecture migration |

---

## 🚀 Quick Start: Creating Milestones

To create all GitHub milestones defined in this roadmap:

```bash
# Dry run first to see what will be created
python scripts/create_github_resources.py --dry-run --all

# Create all milestones and sample issues
python scripts/create_github_resources.py --all
```

**Prerequisites**:
- GitHub CLI (`gh`) installed and authenticated
- Python 3.11+

---

## 📊 Test Coverage Goals

| Module | v0.1.1 | v0.1.2 | v0.1.3 | v0.2.0 | v0.2.3 | v0.3.0 | v1.0.0 |
|--------|--------|--------|--------|--------|--------|--------|---------|
| `config.py` | 90% | 90% | 90% | 90% | 95% | 95% | 95% |
| `topic.py` | 70% | 75% | 80% | 90% | 90% | 90% | 90% |
| `registry.py` | 70% | 75% | 80% | 80% | 85% | 85% | 85% |
| `connect.py` | 70% | 75% | 80% | 80% | 85% | 85% | 85% |
| `plugin/__init__.py` | 80% | 90% | 90% | 90% | 90% | 90% | 90% |
| `cli/*` | 70% | 75% | 80% | 85% | 85% | 85% | 85% |
| `widgets/*` | 50% | 60% | 60% | 75% | 80% | 80% | 85% |
| **Total** | **70%** | **75%** | **80%** | **85%** | **85%** | **88%** | **90%** |

---

## 🛠️ Development Workflow

### Branching Strategy
```
main (protected)
  └── develop
       ├── feature/* (PR to develop)
       ├── bugfix/* (PR to develop)
       ├── release/* (PR to main)
       └── ci-cd (current working branch)
```

### Pull Request Requirements
- [ ] All tests pass
- [ ] Coverage does not decrease below target
- [ ] ruff linting passes
- [ ] mypy type checking passes
- [ ] Documentation updated
- [ ] Changelog entry added (via towncrier)
- [ ] Linked to appropriate milestone

### Release Process
1. **Feature Freeze**: All features for the release must be merged
2. **Test Freeze**: All tests must pass
3. **Documentation Freeze**: All docs must be updated
4. **Release Candidate**: Create RC tag, test extensively
5. **Final Release**: Create vX.Y.Z tag, publish to PyPI
6. **Post-Release**: Update milestones, create next version milestone

---

## 📦 Documentation Plan

| Document | v0.1.1 | v0.1.2 | v0.1.3 | v0.2.0 | v0.2.3 | v0.3.0 | v1.0.0 |
|----------|--------|--------|--------|--------|--------|--------|---------|
| README.md | ✅ Update | ✅ Update | ✅ Update | ✅ Major | ✅ Update | ✅ Update | ✅ Major |
| CONTRIBUTING.md | ✅ Create | ✅ Update | ✅ Update | ✅ Update | ✅ Update | ✅ Update | ✅ Update |
| TESTING.md | ✅ Create | ✅ Update | ✅ Update | ✅ Update | ✅ Update | ✅ Update | ✅ Update |
| Configuration Guide | ❌ | ❌ | ❌ | ✅ Create | ✅ Update | ✅ Update | ✅ Update |
| User Guide | ❌ | ❌ | ❌ | ✅ Create | ✅ Update | ✅ Update | ✅ Update |
| Plugin Development | ❌ | ❌ | ❌ | ❌ | ✅ Create | ✅ Update | ✅ Major |
| CLI Reference | ❌ | ❌ | ❌ | ✅ Create | ✅ Update | ✅ Update | ✅ Update |
| API Reference | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Create |
| Migration Guide | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Create |

---

## 🎯 Priority Matrix

| Priority | Description | Features | Testing | Documentation |
|----------|-------------|----------|---------|---------------|
| **P0 (Critical)** | Blocking issues, must have for next release | Bug fixes, connection handling | Core module tests | README, CONTRIBUTING |
| **P1 (High)** | Important features for next release | Message streaming, CLI | Integration tests | User guides |
| **P2 (Medium)** | Nice to have, can wait for next release | UX improvements, settings | Edge case tests | Reference docs |
| **P3 (Low)** | Backlog items | Advanced features, monitoring | Performance tests | Migration guides |

---

## 💡 Open Questions & Decisions

### To Be Decided
1. **Testing Strategy**: Should we use mocking for Kafka or spin up test containers?
   - *Recommendation*: Use mocking for unit tests, test containers for integration tests

2. **Message Display Format**: How should we handle non-JSON messages?
   - *Recommendation*: Raw display with optional formatting, detect content type

3. **Authentication Storage**: How to securely store credentials?
   - *Recommendation*: Use keyring library or environment variables

4. **REST API Transition**: Full replacement or gradual migration?
   - *Recommendation*: Gradual - add REST API support, keep confluent-kafka as fallback

5. **Plugin Ecosystem**: Should we support external plugins before v1.0?
   - *Recommendation*: Yes, design for extensibility but focus on built-in plugins first

---

## 📞 Support & Contributing

- **Issues**: https://github.com/Timon Viola/lazy-kafka/issues
- **Discussions**: https://github.com/Timon Viola/lazy-kafka/discussions
- **Contributing**: See CONTRIBUTING.md
- **License**: MIT

---

*Current date: 2026-09-12*
*Roadmap owner: @timonviola*
*Total milestones: 9 (v0.1.1 through v1.0.0)

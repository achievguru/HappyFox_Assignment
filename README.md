# 📬 HappyFox_Assignment

This project is a Gmail automation script developed as part of a technical assignment for the Technical Lead – Backend role at HappyFox.

It performs the following:
- Authenticates via OAuth2 with the Gmail API
- Fetches and stores emails in an SQLite3 database
- Applies rules defined in a `rules.json` configuration file
- Executes Gmail actions like marking emails as read or moving them to labels

The codebase is structured for long-term maintainability, readability, and reusability.


# Gmail Rule Processor - Project Structure

## 📁 Clean Project Structure

```
game_rule_processor/
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── main.py                       # Application entry point
├── config.py                     # Configuration management
├── database.py                   # Database operations
├── gmail_auth.py                 # Gmail API authentication
├── gmail_fetcher.py              # Email fetching and parsing
├── rule_engine.py                # Rule evaluation and processing
├── actions.py                    # Gmail actions (mark read, move, etc.)
├── rules.json                    # Rule configuration file
├── integration_testing.py        # Integration tests
└── tests/                        # Unit tests directory
    └── test_rule_engine.py       # Rule engine unit tests
```

## 🧹 Cleanup Summary

### Removed Files:
- ✅ `__pycache__/` directories (Python bytecode cache)
- ✅ `.pytest_cache/` directory (Pytest cache)
- ✅ `gmail_processor.log` (Application log file)
- ✅ `emails.db` (Database file - regenerated on first run)
- ✅ `token.json` (Authentication token - regenerated on first run)

### Added Files:
- ✅ `.gitignore` (Comprehensive ignore rules)
- ✅ `test_integration.py` (Integration tests)

## 📋 File Descriptions

### Core Application Files:
- **`main.py`** - Application entry point with logging and error handling
- **`config.py`** - Centralized configuration management
- **`database.py`** - Database operations with proper connection management
- **`gmail_auth.py`** - Gmail API OAuth 2.0 authentication
- **`gmail_fetcher.py`** - Email fetching and parsing from Gmail API
- **`rule_engine.py`** - Rule evaluation and processing logic
- **`actions.py`** - Gmail actions (mark read/unread, move to labels)

### Configuration Files:
- **`rules.json`** - Rule configuration file (example)
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore rules for clean repository

### Documentation Files:
- **`README.md`** - Project documentation and setup instructions

### Test Files:
- **`test_integration.py`** - Integration tests for core functionality
- **`tests/test_rule_engine.py`** - Unit tests for rule engine

## 🎯 Benefits of Clean Structure

1. **No Unnecessary Files**: Removed cache files, logs, and temporary data
2. **Version Control Ready**: Proper .gitignore prevents committing sensitive data
3. **Professional Appearance**: Clean, organized structure
4. **Easy Setup**: New users can clone and run immediately
5. **Maintainable**: Clear separation of concerns

## 🚀 Ready for Submission

The project is now clean and ready for submission with:
- ✅ All core functionality implemented
- ✅ Comprehensive testing
- ✅ Professional documentation
- ✅ Clean project structure
- ✅ Proper version control setup 

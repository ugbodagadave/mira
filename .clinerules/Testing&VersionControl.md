# Test-First Git Workflow

## Overview
This workflow ensures all code changes are thoroughly tested and properly documented before being committed to the repository. Cline will automatically run tests, verify documentation updates, fix failing tests if needed, and only push code that passes all tests and includes proper documentation.

## Workflow Steps

### 1. After Making Changes or Adding Features
- Run complete test suite on entire codebase
- Wait for test results

### 2. If All Tests Pass
- **Verify documentation is updated** (see Documentation Requirements below)
- Stage all changes: `git add .`
- Commit with descriptive message: `git commit -m "feat/fix: [description]"`
- Push to remote repository: `git push origin [branch-name]`

### 3. If Any Tests Fail
- **DO NOT COMMIT OR PUSH**
- Analyze failing test output
- Identify root cause of test failures
- Fix the failing tests by either:
  - Correcting the implementation code
  - Updating test expectations if they're outdated
  - Fixing test setup/teardown issues
- Re-run complete test suite
- Repeat until all tests pass
- Only then proceed to documentation verification and commit/push

### 4. Documentation Requirements
Before committing and pushing, ensure:
- **README.md** is updated if new features or setup instructions are added
- **files in MemoryBank Directory** is updated for any new endpoints or function signatures
- **bitscrunch-integration** is updated

## Test Commands
```bash
# Run all tests
npm test
# or
yarn test
# or
pytest
# or whatever test command is appropriate for the project
```

## Documentation Commands
```bash
# Generate API documentation (if applicable)
npm run docs
# or
yarn docs

# Check for documentation completeness
npm run docs:check
```

## Git Commands
```bash
# Stage changes
git add .

# Commit with message
git commit -m "descriptive commit message"

# Push to remote
git push origin main
```

## Important Notes
- **Never push failing tests**
- **Never push without updated documentation**
- Always run the full test suite, not just affected tests
- Fix tests immediately when they fail
- Update documentation before committing
- Use descriptive commit messages
- Ensure working directory is clean before starting new features

## Success Criteria
✅ All tests pass  
✅ Documentation is updated and accurate  
✅ Code is committed with clear message  
✅ Changes are pushed to remote repository  
✅ Working directory is clean

## Documentation Checklist
- [ ] README.md updated (if applicable)
- [ ] MemoryBank Files updated (if applicable)
- [ ] bitscrunch-integration updated (if applicable)
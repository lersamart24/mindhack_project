# Git Workflow Guide

## Repository
`https://github.com/lersamart24/mindhack_project.git`

---

## Basic Workflow (with branch)

### 1. Make sure you are on main and up to date
```bash
git checkout main
git pull origin main
```

### 2. Create and switch to a new branch
```bash
git checkout -b your-branch-name
```
Example: `git checkout -b feature/battle-update`

### 3. Stage your changes
```bash
# Stage specific files
git add file1.py file2.py assets/image.png

# Stage everything (avoid adding __pycache__)
git add .
```

### 4. Commit your changes
```bash
git commit -m "Short description of what changed"
```

### 5. Push the branch to GitHub
```bash
git push origin your-branch-name
```

### 6. Open a Pull Request on GitHub
Go to `https://github.com/lersamart24/mindhack_project` and click **"Compare & pull request"**.

---

## Useful Commands

| Command | Description |
|---|---|
| `git status` | See what files have changed |
| `git branch` | List all local branches |
| `git branch -a` | List all branches (local + remote) |
| `git checkout main` | Switch back to main branch |
| `git log --oneline -5` | See last 5 commits |
| `git diff` | See unstaged changes |

---

## Branch Naming Conventions

| Prefix | Use for |
|---|---|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `assets/` | Art or asset updates |
| `docs/` | Documentation changes |

Example: `feature/new-enemy`, `fix/battle-crash`, `assets/sprite-update`

---

## Files to Never Commit
- `__pycache__/` — Python compiled files
- `*.pyc` — Python bytecode
- `.env` — Secret keys or passwords

Add these to `.gitignore` to keep them out automatically.

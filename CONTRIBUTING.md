# Contributing Guide

## Project Overview

This project is a Personal Expense Tracker developed using Python, Flask, HTML, CSS, and JavaScript.

## Team Members

The project was developed collaboratively by two students.

## Branching Strategy

Each student used a separate feature branch to develop and test features.

- `main`: Contains the integrated project.
- `feature-member1`: Contains Student 1's features.
- `feature-member2`: Contains Student 2's features.

## Individual Contributions

### Student 1 — ravii

- Developed expense reports.
- Added CSV export functionality.
- Added month and category filters.
- Improved expense summaries.
- Created and reviewed pull requests.

### Student 2

- Implemented expense editing.
- Added restore functionality.
- Worked on the merge conflict resolution.
- Created and reviewed pull requests.

## Pull Requests and Code Reviews

Both students used pull requests to propose changes.

Each student reviewed the other student's changes before merging. The team merged both feature branches into `main`.

## Merge Conflict Resolution

Both students modified a shared line in `app.py`. Git reported a merge conflict because the changes affected the same line.

The team resolved the conflict by keeping one combined initialization comment:

```python
app = Flask(__name__) # Initialized collaboratively by Student 1 and Student 2
```

The resolved changes were committed and merged into `main`.

## Commit Guidelines

Use clear commit messages that describe the change.

Examples:

- `Add CSV export for expenses`
- `Add expense editing functionality`
- `Resolve merge conflict with Student 1`

## Reporting Issues

Report any bugs or unexpected behavior to the project team. Include the steps to reproduce the issue and the expected result.

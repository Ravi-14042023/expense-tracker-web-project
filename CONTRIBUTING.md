# Contributing Guide

This document records the Git and GitHub workflow followed by the two members of the **SEC101 MCA Group Assignment**.

## Team Members

| Student | Name | Roll number | GitHub account | Feature branch |
| --- | --- | --- | --- | --- |
| Student 1 | **Ravindra Kilaniya** | **48** | [Ravi-14042023](https://github.com/Ravi-14042023) | `feature-member1` |
| Student 2 | **Tejaswi Rawal** | **61** | [Tejaswi-06-24](https://github.com/Tejaswi-06-24) | `feature-member2` |

## Branching Strategy

- `main` — The integrated project containing reviewed and merged features.
- `feature-member1` — Ravindra's development branch for expense reporting and CSV export.
- `feature-member2` — Tejaswi's development branch for editing and restoring expenses.

Both students used their own GitHub accounts. Changes were developed in feature branches rather than committed directly to `main`.

## Individual Contributions

### Student 1 — Ravindra Kilaniya (Roll No. 48)

- Created and maintained the GitHub repository.
- Added the expense reports page and category-wise spending information.
- Implemented month and category summary filters.
- Added CSV export for active expenses.
- Fixed the missing month key in the monthly summary.
- Created [PR #1](https://github.com/Ravi-14042023/expense-tracker-web-project/pull/1) and reviewed Student 2's pull request.

Selected feature commits:

| Commit | Work |
| --- | --- |
| [`5298a93`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/5298a93) | Fix missing month key in monthly summary |
| [`9768020`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/9768020) | Add month and category filters to expense summary |
| [`4198bd3`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/4198bd3) | Add expense reports page |
| [`1de5f82`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/1de5f82) | Add CSV export for expenses |

### Student 2 — Tejaswi Rawal (Roll No. 61)

- Implemented the expense-editing backend and prefilled Edit Expense form.
- Added **Edit** buttons to the expense list.
- Implemented the **Restore All** backend for soft-deleted expenses.
- Added the Restore All control and related tests.
- Created [PR #2](https://github.com/Ravi-14042023/expense-tracker-web-project/pull/2) and reviewed Student 1's pull request.
- Participated in merge-conflict demonstration and recorded the resolution commit.

Selected feature commits:

| Commit | Work |
| --- | --- |
| [`b1b3331`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/b1b3331) | Implement expense editing backend and form |
| [`687330d`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/687330d) | Add Edit buttons on expense list |
| [`6c6b914`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/6c6b914) | Implement Restore All backend |
| [`36ee029`](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/36ee029) | Add Restore All button and tests |

## Pull Requests and Peer Reviews

| PR | Author | Reviewer | Main purpose |
| --- | --- | --- | --- |
| [#1 — Reports and CSV export](https://github.com/Ravi-14042023/expense-tracker-web-project/pull/1) | Ravindra | Tejaswi | Integrate report, category/month summary and export changes |
| [#2 — Edit Expense and Restore All](https://github.com/Ravi-14042023/expense-tracker-web-project/pull/2) | Tejaswi | Ravindra | Integrate expense-editing and recovery changes |

**Review process:**

1. Each student pushed their separate feature branch to GitHub.
2. Each student opened a pull request targeting `main`.
3. The other student inspected the changes and submitted a code review.
4. The group coordinated the merge-conflict demonstration and final integration.
5. Reviewed changes were merged into `main` after the conflict was resolved.

## Demonstration of a Merge Conflict

Both students modified the same Flask initialisation line in the shared `app.py` file on separate branches.

- Student 1 added a comment identifying Ravi.
- Student 2 added a different comment identifying Student 2.
- After the first feature branch was merged, Student 2 attempted to merge `origin/main` into `feature-member2`.
- Git reported `CONFLICT (content): Merge conflict in app.py`.
- Both students agreed to retain one shared line rather than two Flask application initialisations.

The final resolved line in `app.py` was:

```python
app = Flask(__name__) # Initialized collaboratively by Student 1 and Student 2
```

The resolution was saved in commit [`002fcd6` — Resolve merge conflict with Student 1](https://github.com/Ravi-14042023/expense-tracker-web-project/commit/002fcd6).

Screenshots of the terminal conflict, conflict markers, corrected file, pull-request approvals and commit graph are included in the group PDF report.

## Contribution Workflow for Future Changes

Before creating a new branch, work from an up-to-date `main`:

```bash
git switch main
git pull origin main
git switch -c feature-descriptive-name
```

After implementing and testing a meaningful change:

```bash
git status
git add <changed-files>
git commit -m "Describe the actual change"
git push -u origin feature-descriptive-name
```

Then open a PR into `main`, ask the other team member to review, address feedback and merge only when the changes have been checked.

## Coding and Review Guidelines

- Keep changes limited to the task assigned to the branch.
- Use clear commit messages that explain **what changed**.
- Test expense creation, editing, deletion, recovery and reporting after modifying shared routes.
- Resolve conflicts carefully so neither student's code is accidentally lost.
- Keep `README.md` and `CONTRIBUTING.md` updated with actual features and evidence links.
- Never commit passwords, API keys, `.venv/`, `.env` files or `expenses.db`.

## Testing

The Student 2 contribution added tests in `tests/test_student2_features.py`. From the project folder, run:

```bash
python -m unittest discover -s tests -v
```

Also verify the user-facing workflows in the browser, particularly **Edit Expense**, **Recycle Bin → Restore All**, **Reports** and **CSV export**.

## Reporting Issues

When reporting a bug, include a brief description, steps to reproduce it, what you expected, what actually happened and any relevant screenshots. Do not attach private expense data or secrets.

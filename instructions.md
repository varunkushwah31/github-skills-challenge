# Instructions for this task

Follow these steps manually in the terminal. Do not commit or push without explicit approval.

## 1) Set up the local environment

```bash
cd /workspaces/github-skills-challenge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest==8.4.1 pytest-cov coverage==7.9
```

## 2) Run the test suite and check coverage

```bash
cd /workspaces/github-skills-challenge
source .venv/bin/activate
python -m pytest -q -vv --cov=src --cov-report=term-missing
```

Confirm:
- all tests pass
- coverage meets the required threshold for the workflow
- no application logic is modified to force coverage higher

## 3) Review the repository changes

Check the files below before committing:
- .github/workflows/python-tests.yml
- .github/workflows/python-coverage.yml
- README.md if needed
- any code or tests you intentionally changed

## 4) Create or update the CI workflows

The workflows should:
- trigger on pull requests targeting main
- run on ubuntu-latest
- install dependencies
- run pytest with verbose output
- generate coverage data for src
- publish coverage as a PR comment
- fail if coverage is below the required minimum

## 5) Commit only when you are ready

When you want to save the work, run:

```bash
git status
git add <files>
git commit -m "Describe the change"
```

Then push only if you want to publish:

```bash
git push origin main
```

## 6) Final verification before submission

- confirm the workflow files exist in .github/workflows/
- confirm GitHub Actions recognizes them
- confirm the pull request triggers both workflows
- confirm tests pass on GitHub
- confirm coverage comment appears on the PR
- confirm the minimum coverage requirement is enforced

## Important rule

I will not create a commit or push by myself. Please tell me when you want me to make a file change, and I will provide the exact next step. If you want changes applied, I will edit files only after your approval.

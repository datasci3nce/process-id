# Publish to GitHub

Repository: `datasci3nce/process-id` (public).

## 1. Create the empty repository
Open https://github.com/new and choose owner `datasci3nce`, repository name `process-id`, visibility **Public**. Leave the initialization options empty (do not add a README, .gitignore, or license; those are supplied here).

## 2. Push this extracted directory
Extract `process-id-github-ready.zip` to a local directory, open a terminal in it, and run:

```bash
git init -b main
git add .
git commit -m "Initial public research release: code, results, and two draft papers"
git remote add origin https://github.com/datasci3nce/process-id.git
git push -u origin main
```

GitHub may request authentication (Git Credential Manager or a credential helper). Do not paste a personal access token into this repository.

## After publishing
Confirm the two manuscripts at `papers/` and experiment source at `experiments/`. The ZIP itself should **not** be uploaded as a single file; GitHub will not unpack it. The archived evaluator-only labels, private execution ledgers and external raw Wiki data are deliberately excluded.

This repository deliberately has **no LICENSE file** until the author selects a license. Public visibility alone does not grant an open-source license.
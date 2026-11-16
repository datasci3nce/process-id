# Complete the experiment-code upload

The **public GitHub repository already exists** at https://github.com/datasci3nce/process-id and has a README, research-lineage document and revised papers. The experiment source tree is still incomplete.

The complete reviewed release snapshot is provided separately as `process-id-github-ready-with-prior-work.zip`.

## Upload the remaining files locally

1. Download and extract the reviewed ZIP.
2. Run these commands inside the extracted root. They preserve the existing repository and push only the files in the reviewed snapshot.

```bash
git clone https://github.com/datasci3nce/process-id.git
cd process-id
# Copy the extracted snapshot contents here, preserving the experiments/ and papers/ directories.
git add .
git status
git commit -m "Add vetted experiment source, tests, summaries and figures"
git push origin main
```

If `git status` shows unexpected additions (private ledger, original evaluator-only label, API key, raw external Wiki export), **do not commit**. Never commit credential files or full raw experimental archives.

Once all files are committed, revise the repository README to point to the actual code locations. The earlier TPRN repo is a separate historical artifact and does not need to be duplicated.

# Public release status and reproduction notes

The vetted code-and-results snapshot was committed to the public [process-id repository](https://github.com/datasci3nce/process-id) on 16 November 2026. This repository includes two **working** manuscript drafts, source code, tests, selected synthetic and aggregate outputs, and figures.

The original historical TPRN, PO-ID, IPN and SWARM-HUNT code archives remain separate; see [docs/PRIOR_RESEARCH_LINEAGE.md](docs/PRIOR_RESEARCH_LINEAGE.md). Public source bytes for the external Wiki graph and evaluator-only truth/ledger files are intentionally excluded.

## Checking the local release

```bash
git clone https://github.com/datasci3nce/process-id.git
cd process-id
find experiments -name 'test_*.py' -print
```

Individual experiments have separate dependencies and frozen protocols. Their README files describe how to run tests and the limitations of replaying aggregate reports. **Not every result can be independently replayed from this repository alone.**

No open-source license has yet been selected. Repository visibility does not override the data-rights restrictions documented in [DATA_POLICY.md](DATA_POLICY.md).

Avoid uploading original ZIP packages, generated private SQLite ledgers, raw evaluator-only labels or API credentials to the repository.

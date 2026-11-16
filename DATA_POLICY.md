# Public data policy and withheld materials

This repository includes code and aggregate outputs while withholding evaluator-only truths and unblinded results that would compromise future blind testing. The original full research bundle is retained separately by the author.

**Deliberately withheld:**
- PROCESS-ID-0.2 and 0.3 `private_ledgers/`, `sandbox_artifacts/`, and evaluator-only masked cases, world labels, stress-truth rows and acquisition traces.
- All scale1 and DELAY-PERC evaluator-only labels, native private histories, heldout scored outputs and per-row model predictions.
- Per-case Wiki evaluation datasets and selected raw extracts, third-party Wiki bodies and derived graph edge list.
- Nested archival ZIPs (which may contain evaluator-only truth), Google Colab notebook outputs, temporary files and local secrets.

**Interpretation:** JSON summary files and plots may contain aggregate metrics computed with private truth. They are *not* blinded evaluation files. Source scripts may regenerate synthetic truth locally but should not load private original evaluation results from this public repository.

**Full live run:** The user's 24-world OpenRouter results are stored separately on their Google Drive and are not represented in the source snapshot; only earlier code and user-reported diagnostics are available.

**Third-party provenance:** Any reanalysis of Collusion Wiki and published derived graph must fetch independently and respect the original owners' permissions and license terms; neither dataset is bundled or relicensed.
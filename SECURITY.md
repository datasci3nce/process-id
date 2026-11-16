# Security and disclosure guidance

Never commit API keys, Colab Secrets, `.env` files, private execution ledgers or hidden evaluation labels. If a credential was previously exposed, revoke it with its provider before releasing any repository. The public snapshot was screened using literal-token patterns but **automated screening cannot guarantee absence of all secrets**.

Do not infer specific actor identities, private intentions, directed provenance or agent misconduct from shared names, URLs or temporally close public traces. Keep candidate reconstruction distinct from evidential justification.
# CE–Recoverability-1: Can causal emergence and evidence recoverability diverge?

**Date:** 2026-11-15  
**Status:** Executed exact finite-state reference experiment; hypothesis-generating only  
**Scientific scope:** CE 2.0-style *fixed-path* causal-primitives analysis versus exact observed-only identifiability. **Not** a full CE 2.0 lattice search, causal discovery method, or LLM-agent evaluation.

## Executive result

**Yes, the two quantities diverge in a deliberately small, exact counterexample.** Changing *only nuisance-variable dynamics* changes the measured causal-power increments along an 8→4→2 state coarse-graining, while leaving the target macrostate's exact evidence recoverability and Bayes-optimal probabilistic predictions unchanged. Evidence deletion can make even a causally strong macrostate entirely unidentifiable. An all-random system shows higher *macro than micro recoverability* solely because the macro claim is simpler, despite zero causal power at all scales.

These examples disprove a naive identity or monotonic relationship between the selected causal-power measure and evidence recoverability. They **do not** establish that the two are generally statistically independent, or that real multi-agent systems exhibit causal emergence.

## Prior work and exact CE 2.0 boundary

Hoel, *Quantifying emergent complexity*, *Patterns* 7(1), 101472, January 9, 2026 (DOI `10.1016/j.patter.2025.101472`) studies increments in causal power along a micro-to-macro path and the attribution of causal contributions across scales. The authors' toolkit, PyMergence, provides `suff_plus_nec` and `effectiveness` modes. We independently implement their formulas for the two measures on **one prespecified, valid coarse-graining path**; we do **not** search the full partition lattice, choose an optimal path, or compute the full multiscale emergent-complexity quantity. In particular, normalized effectiveness can be flat where `sufficiency + necessity − 1` grows: we include both rather than treating them as equivalent.

- Paper: https://doi.org/10.1016/j.patter.2025.101472
- Preprint: https://arxiv.org/abs/2503.13395
- Toolkit: https://github.com/EI-research-group/pymergence/tree/6e5cb45bf445a29e8c5fb7b2a01c56efbc6e06ef
- Toolkit formula inspected: `pymergence/StochasticMatrix.py` methods `suff_plus_nec`, `average_sufficiency`, `average_necessity`, `effectiveness`.

### Causal primitives and intervention semantics

For a row-stochastic transition matrix \(P\) with \(n\) states, using **uniform interventions over present states**:

\[
\mathrm{Suff}(P)=\frac1n\sum_{c,e}P_{ce}^{2},\qquad
\mathrm{Nec}(P)=\frac1n\sum_{c,e}P_{ce}\left[1-\frac{\sum_{c'\ne c}P_{c'e}}{n-1}\right],
\]

\[
\boxed{\mathrm{CP}_{\mathrm{SN}}(P)=\mathrm{Suff}(P)+\mathrm{Nec}(P)-1.}
\]

The sensitivity analysis uses the toolkit's normalized effectiveness, \(\mathrm{CP}_{\mathrm{eff}}(P)=I_{U}(X_t;X_{t+1})/\log_2 n\). These are **intervention-defined transition quantities**, not observational model scores. We do not claim that they alone measure *all* aspects of causation in a deployed system.

## Exact setup

Each microstate consists of three bits \(X_t=(M_t,A_t,B_t)\), with 8 possible states and 3 time steps \(t=0,1,2\). Initially all 8 microstates are equally likely. Bits evolve independently:

\[
P(X_{t+1}\mid X_t)=\prod_{j\in\{M,A,B\}}\left[q_j\,\mathbf 1\{X_{j,t+1}=X_{j,t}\}+(1-q_j)\,\mathbf 1\{X_{j,t+1}\ne X_{j,t}\}\right].
\]

The **predeclared** nested coarse-graining is \((M,A,B)\to(M,A)\to M\) (8→4→2 states). It is *strongly lumpable*: every microscopic state within a macro block induces **exactly the same distribution** over subsequent macro blocks. This is verified in code, not assumed.

The epistemic target is whether the value \(T=M_2\), as distinct from the entire microstate \(X_2\), is uniquely determined by available evidence. There are 9 possible observations: each of the 3 bits at each of the 3 steps. Observations are precise and truthful when retained; missing values are unknown. Observing a bit is not intervening on the dynamics.

**Three observation mechanisms:** (i) each of 9 observations retained independently with probability \(p\); (ii) all three time observations of a bit retained/dropped as one source group with probability \(p\); (iii) all macro-bit observations inaccessible, while nuisance observations are independently retained. These are mathematically distinct missingness models, not interchangeable.

We exhaustively enumerate **all 512 micro histories**, **512 independent masks**, **8 component-group masks**, and **64 target-blind masks**, for six process mechanisms. The resulting 3,504 mask/model combinations are each evaluated over *all possible retained evidence values*, with their exact probabilities—not a single hidden sampled history. Integrating over masks at seven retention settings yields 126 recovery-curve rows. There is no model fitting, held-out test, or statistical sampling error to attach a confidence interval to these deterministic calculations.

### Identifiability and probabilistic scoring

Let \(\mathcal C(O_m)\) include all histories of strictly positive transition probability compatible with observations \(O_m\). Claim identification is the exact condition:

\[
I_M(O_m)=\mathbf 1\Big[\left|\{M_2(H):H\in\mathcal C(O_m)\}\right|=1\Big].
\]

The exact recoverability curve averages this indicator over both the native history distribution and the evidence-mask distribution, not over a chosen estimator's outputs. **Bayes Brier** is independently computed as \(\mathbb E[P(M_2=1\mid O_m)\{1-P(M_2=1\mid O_m)\}]\); it measures optimal posterior prediction risk rather than certification. A high posterior probability does not imply unique support.

## Results A — the target-matched causal-emergence counterexample

The most informative models have the **same macro-bit transition** (\(q_M=0.92\)) but different nuisance dynamics:

| Micro dynamics (qM,qA,qB) | CE2 suff+nec micro | Meso | Macro | Fixed-path net ΔCP | Normalized-effectiveness net Δ |
|---|---:|---:|---:|---:|---:|
| Emergent stochastic (.92,.50,.50) | 0.100800 | 0.235200 | 0.705600 | **+0.604800** | +0.398547 |
| Isotropic stochastic (.92,.92,.92) | 0.565959 | 0.636357 | 0.705600 | +0.139641 | 0.000000 |
| Declining-path control (.92,1,1) | 0.831771 | 0.803733 | 0.705600 | **−0.126171** | −0.268119 |

The two stochastic controls illustrate why it is necessary to specify the causal-power definition. The declining-path control has no **positive increment along this tested path**; this does not rule out emergence somewhere else in the lattice.

**Every one of these three models has precisely the same posterior for \(M_2\), support-based certification, and exact recovery curves under each observation mechanism**. For example, at independent retention \(p=.5\):

| Model | Exact macro identification | Bayes Brier | Exact full microstate identification |
|---|---:|---:|---:|
| Emergent stochastic | 0.500000 | 0.065342 | 0.125000 |
| Isotropic stochastic | 0.500000 | 0.065342 | 0.125000 |
| Declining-path stochastic | 0.500000 | 0.065342 | 0.382812 |

The macro claim is identical across these cases; the full-microstate task is **different** and shows the impact of nuisance-bit persistence. This is why comparing only macro vs micro accuracy would be insufficient.

**Reason the matching result holds:** Both the trajectory distribution and observation process factor by bit. Therefore \(P(M_2\mid O_M,O_A,O_B)=P(M_2\mid O_M)\); changing \(q_A,q_B\) can change causal primitives of the *whole* system without changing any claim about \(M_2\) conditional on its retained observations. This is a constructive demonstration, not an unexplained numerical coincidence.

## Results B — high causal-power gain can coexist with poor epistemic access

Two models have deterministic macro-bit dynamics, \(q_M=1\):

| Model | CE2 suff+nec fixed-path net ΔCP | Macro identification at p=.25, independent | Macro identification at p=.5, independent |
|---|---:|---:|---:|
| Emergent deterministic (1,.5,.5) | **+0.857143** | 0.578125 | 0.875000 |
| All-deterministic control (1,1,1) | 0.000000 | 0.578125 | 0.875000 |

With independent observations, a single retained macro-bit observation at any time determines \(M_2\), so \(R_M(p)=1-(1-p)^3\). If the macro observations are lost as a single source group instead, \(R_M(p)=p\). With the entire macro evidence channel inaccessible, \(R_M=0\) for every \(p\), even when the causal-power increment is +0.857. The statement concerns **observability**, not disappearance of underlying causal influence.

## Results C — easier coarse prediction does not establish emergence

For the all-random negative control \(q=(.5,.5,.5)\), causal power is zero at 8, 4 and 2 states under both measures. Nevertheless, at independent \(p=.5\), the macro claim is identified with probability **0.500**, compared with **0.125** for the entire microstate. This is simply because the macro claim asks for one observed bit and the microstate asks for three. It is a *task-difficulty control*, **not** evidence of emergence.

## Analytical checks and percolation connection

For a stochastic macro-bit with both transitions possible and strictly positive (\(0<q_M<1\)), missing its final observation always leaves both outcomes compatible, hence \(R_M^{\rm independent}(p)=p\). For a deterministic macro-bit (\(q_M=1\)), observations from any of three times suffice, giving \(R_M^{\rm independent}(p)=1-(1-p)^3\). If all macro observations are a single jointly erased group, \(R_M^{\rm grouped}(p)=p\) in both regimes. These identities were verified against exhaustive latent-history enumeration for every reported retention probability.

This is a finite **evidence-reliability** calculation closely related to percolation, not a demonstrated critical phase transition. No PDE or DDE was fitted: a finite discrete Markov chain was chosen to make causal and epistemic quantities exact.

## Falsification audit

1. Both causal-primitives and normalized-effectiveness modes are calculated; conclusions are not selected from one score without disclosure.
2. Two chosen coarse-grainings are **dynamically consistent** by strong lumpability.
3. All states, transitions, histories, observation values, and masks are integrated exactly.
4. Causal power uses uniform *interventions*; recoverability uses the model's *native history distribution* and independently drawn evidence deletion. These are deliberately different quantities.
5. The macro claim and observation channels are **fixed** in the primary stochastic controls; only nuisance dynamics change.
6. Null controls include all random, all deterministic, and total macro-channel blindness.
7. Complete-microstate identification and macrostate identification are separately reported so easy aggregation is not mistaken for emergence.
8. The experiment does not search the full CE2 causal path space, learn causal relationships, or test real agent traces. The selected coarse-graining is one of many possible choices. The positive increment is not asserted to be an original discovery about CE 2.0.
9. Values are exact *within the declared model*, not robust to a misspecified class of histories or an unreliable observation channel.
10. Reproduction involves no random seed, GPU, web downloads, or hidden evaluator files. Both the independent and explicit-loop causal-primitives computations are tested.

## Scientific conclusion and publication decision

**Causal contribution across scales and claim-specific epistemic recoverability are distinct axes.** A macro description can gain substantial measured causal power even if its target claim is neither more nor less identifiable from a fixed observation process; conversely, a simpler target can be easier to identify with no gain in causal power. Missingness correlations and sensor placement can change recoverability while leaving native dynamics and their causal power untouched.

This is a *controlled theoretical sanity check*, not enough for a standalone research paper and not evidence of causal emergence in multi-agent LLM behavior. The next legitimate experiment would use a small **instrumented multi-agent system with interventionally supported micro/meso variables and truly variable evidence access**, retaining exact or independently validated process histories. Do not put these post-sprint toy results into the already-finished November 13–15 sprint paper without identifying them as new follow-up work.

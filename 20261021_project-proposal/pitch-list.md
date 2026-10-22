# CPSC 4710 Project: Pitch List for Team Meeting (Oct 14, 2026)

Constraints these ideas were built around:
- Team of 3. Each person writes their own method and experiment section, so every idea splits into 3 pieces.
- Mixed coding skill, so each idea has heavy and light pieces.
- Image classifiers only.
- Proposal due about Oct 21, milestone Nov 13, final report Dec 16.
- YCRC cluster for compute.

Every idea has an **ensemble attack** at its core. That attack is listed in Lecture 8 but wasn't taught: craft one perturbation that fools several white-box surrogate models together, then transfer it to an unseen black-box target.

---

## A. Ensemble attacks × explainability

### 1. Explanation hijacking without seeing the model (Grad-CAM, IG, LIME)
**Pitch.** People use explanations like Grad-CAM as a trust check ("the model looked at the tumor, not the ruler"). Known attacks can warp an explanation while keeping the prediction the same, but they need the target's gradients or thousands of queries. We build the perturbation on an ensemble of public models *and* explainers, then test whether it warps an unseen target's explanation. We also test the reverse: flip the label while keeping the explanation looking normal, which defeats explanation-based sanity checks.

**3-way split:**
- Heavy: ensemble map-shift attack and cross-architecture transfer matrix.
- Medium: "stealth" label-flip variant.
- Light: which explainers on the target are vulnerable (Grad-CAM, IG, SmoothGrad, RISE, LIME), run with Captum or pytorch-grad-cam.

**Novelty: medium-high.** The closest work is white-box (Dombrowski '19), query-based (AttaXAI '23) or CLIP-only (X-Shift '26).

**Risk.** Explanation attacks may barely transfer; ADV² ('20) saw weak transfer across interpreters. A measured transfer matrix is still a benchmark contribution.

**Lectures:** 4, 6, 8.

### 2. Which surrogates matter? Shapley values over the ensemble (SHAP, LIME) ⭐ recommended
**Pitch.** Treat each surrogate model as a player in a cooperative game whose payoff is fooling *unseen* models. Shapley values show who contributes. Interaction scores show which pairs are redundant (two ResNets) and which are synergistic (a CNN plus a ViT). Then test whether cheap explanation similarity predicts those values well enough to pick a small, strong ensemble, for example LIME or RISE maps of the black-box target from a few hundred queries. This also answers a practical question: is ensemble transfer driven by the member *closest* to the target, or by *coverage* from diverse members?

**3-way split:**
- Heavy: coalition-attack engine and Shapley/interaction estimates, run as YCRC job arrays.
- Light: explanation proxies and the correlation study.
- Medium: selection method against baselines (random-k, all models, top-k by accuracy, AdaEA).

**Novelty: medium.** SEAA (ICME '24) already reweights surrogates by Shapley value during the attack. Bad Citrus ('22) uses LIME-based similarity to pick a *single* surrogate. Our new angle has three parts: valuation on held-out targets, pairwise interactions, and explanation-based selection of a whole ensemble.

**Risk: low.** If the proxies fail, the valuation and synergy benchmark is still a result. Start on CIFAR-10, where evaluating many coalitions is cheap.

**Lectures:** 5, 4, 8.

### 3. Attack the concepts all models share (universal sparse autoencoders, SAEs)
**Pitch.** Different networks don't share neurons, which is partly why their gradients disagree. Universal SAEs (2025) learn one dictionary of human-readable concepts ("stripes", "wheel") shared across several vision models. We perturb an image to erase the class's shared concepts in every surrogate at once, betting that the unseen model relies on them too. Every transfer success or failure is then explainable in concept terms.

**3-way split:**
- Heavy: universal SAE training and the concept-space attack.
- Medium: does disrupting shared concepts predict transfer, including for existing attacks?
- Light: baselines and ablations in the TransferAttack repo, plus concept visualizations.

**Novelty: medium-high.** We found no concept-space ensemble attack.

**Risk: highest infrastructure risk.** Universal SAE training reportedly takes about 3 GPU-days, and we couldn't find public code. Fallback: train one SAE per model and match concepts across models.

**Lectures:** 7, 6, 8.

---

## B. Pure ensemble-attack methods

### 4. One perturbation for both normal and adversarially trained targets
**Pitch.** Attacks built on normal surrogates barely dent adversarially trained ("robust") targets. Robust surrogates help against robust targets but hurt against normal ones. Free checkpoints exist at a whole ladder of robustness levels (madrylab ImageNet models). We build ensembles spanning that ladder and learn how to weight or schedule them (for example, robust surrogates early in the attack and standard ones late) so that one perturbation fools both kinds of target.

**3-way split:**
- Light: sweep of ladder mixes and the trade-off frontier.
- Medium: weighting and scheduling methods.
- Heavy: cheap robust fine-tuning of ViT/ConvNeXt surrogates.

**Novelty: medium-high.** Prior work studies *single* robust surrogates. TransferBench (NeurIPS '25) lists robust targets as a setting where current methods fail.

**Risk.** Success on robust targets may sit near the floor. Fallback: CIFAR-10 RobustBench models.

**Lectures:** 9 (adversarial training, TRADES), 8.

### 5. When surrogates disagree: does fixing the conflict help *transfer*, or just *fit*?
**Pitch.** Surrogate gradients point in nearly unrelated directions. Multi-task learning has many "gradient surgery" tools for this kind of conflict (CAGrad, Nash-MTL, UPGrad), and there are worst-case objectives too (CVaR, tilted loss). But the attacker cares about the unseen model (generalization), not the surrogates (training fit). We run a controlled, equal-compute test of whether these tools improve transfer or just overfit the ensemble, using a held-out "validation surrogate" for tuning and early stopping.

**3-way split:**
- Light: drop-in aggregators via the TorchJD library.
- Medium: a family of losses running from average to worst case.
- Heavy: validation-surrogate tuning, fit-vs-transfer diagnostics and robust targets.

**Novelty: medium.** PCGrad- and MGDA-style ensemble attacks exist with small gains (Bag of Tricks '24, TA-MOO '23). The newer aggregators and the fit-vs-transfer framing appear untested.

**Risk.** PGD's sign step may erase differences between aggregators. "A tuned average wins" is still a clean finding. This is the easiest idea to execute.

**Lectures:** 8.

---

## C. Ensemble attacks × other lecture topics

### 6. Do query-attack defenses survive hybrid ensemble attacks? (query-based attacks)
**Pitch.** Some defenses are built to stop attackers who send thousands of near-identical queries: random input noise, scrambled output scores, and query-history detectors like Blacklight. Hybrid attacks (BASES, GFCS) do most of the work on a local surrogate ensemble and query the target only a handful of times. We test whether those defenses still hold, build a defense-aware hybrid attack, and try a "moving-target" defense that answers each query with a randomly chosen model from a pool.

**3-way split:**
- Heavy: defense-robust hybrid attack.
- Light: port 3 defenses into TransferBench and benchmark the existing attacks.
- Medium: moving-target defense plus an adaptive (EOT) evaluation of it.

**Novelty: medium-high.** These defenses were tested mainly against pure query attacks.

**Risk.** TransferBench found that query refinement adds little over pure transfer. If so, these defenses may be irrelevant to hybrid attacks, which is itself a "false sense of security" finding.

**Lectures:** 8 (gradient-estimation attacks, query reduction), 9 (randomized defenses, EOT).

### 7. Honeypot surrogates: booby-trapping the public model zoo (backdoors and poisoning)
**Pitch.** Transfer attackers download public pretrained models to build their ensembles. A defender could publish a "honeypot" model whose gradients carry a secret key, so any attack crafted with it leaves a faint fingerprint the defender can detect. Does the fingerprint survive being averaged with honest models? Do smart ensemble attacks, which re-weight surrogates, filter it out on their own?

**3-way split:**
- Heavy: honeypot training.
- Medium: attack benchmark across honeypot mixes and ensemble methods.
- Light: an adaptive attacker that screens out honeypots, Neural Cleanse-style.

**Novelty: medium-high.** Prior trapdoor work places traps in the *deployed* model, not in public surrogates.

**Risk: highest.** Averaging may wash out the signal. Fallback: report how fast it washes out.

**Lectures:** 9 (backdoors, "pretrained model" attack scenario, Neural Cleanse), 8.

---

## Considered and dropped
- **Perturbing where surrogates' attributions agree:** already done (CAM Ensemble Attack, NDSS '24; NAMEA, AAAI '26).
- **Attacking AI-image watermarks or detectors with ensembles:** already done ('24–'25 papers).
- **Ensemble-crafted clean-label poisons:** crowded, and needs about 60 GPU-hours of victim retraining.
- **Diversity ensemble defenses (DVERGE, TRS) vs. modern ensemble attackers:** a real evaluation gap but medium novelty. A solid backup option.

## Caveat
The novelty checks were about an hour of literature search per lane. These were verified directly: SEAA, the NDSS '24 CAM ensemble paper, universal SAEs, X-Shift and TransferBench. Some other details were confirmed only at abstract level, such as specific numbers in RobustBlack and the exact methods in TA-MOO. Do a focused literature review on whichever idea you choose before the proposal.

## Key references
- Ensemble attack origin: Liu et al. ICLR '17: https://arxiv.org/abs/1611.02770
- Code hubs:
  - TransferAttack (Ens, SVRE, AdaEA, CWA, SMER): https://github.com/Trustworthy-AI-Group/TransferAttack
  - TransferBench: https://github.com/pralab/transfer-bench
  - RobustBench: https://robustbench.github.io
- Idea 1:
  - Dombrowski '19: https://arxiv.org/abs/1906.07983
  - AttaXAI: https://arxiv.org/abs/2211.14860
  - ADV²: https://arxiv.org/abs/1812.00891
  - X-Shift: https://arxiv.org/abs/2605.16651
- Idea 2:
  - SEAA (ICME '24): https://www.semanticscholar.org/paper/Shapley-Ensemble-Adversarial-Attack-Wang-Tang/24aa60580b81466dc689443f0bf27cc2027de44d
  - Bad Citrus: https://arxiv.org/abs/2210.03239
  - Ensemble diversity theory: https://arxiv.org/abs/2410.06851
- Idea 3:
  - Universal SAEs: https://arxiv.org/abs/2502.03714
  - SAE tooling: https://github.com/KempnerInstitute/overcomplete
- Idea 4:
  - RobustBlack: https://arxiv.org/abs/2412.20987
  - madrylab robust ImageNet models: https://huggingface.co/madrylab/robust-imagenet-models
  - TransferBench paper: https://neurips.cc/virtual/2025/poster/121411
- Idea 5:
  - TorchJD: https://github.com/TorchJD/torchjd
  - Bag of Tricks: https://arxiv.org/abs/2401.08734
  - TA-MOO: https://arxiv.org/abs/2304.13229
- Idea 6:
  - BASES: https://arxiv.org/abs/2208.03610
  - Blacklight: https://sandlab.cs.uchicago.edu/blacklight/
  - RND: https://arxiv.org/abs/2104.11470
  - AAA: https://arxiv.org/abs/2205.12134
- Idea 7:
  - Trapdoor: https://arxiv.org/abs/1904.08554
  - BackdoorBench: https://github.com/SCLBD/BackdoorBench

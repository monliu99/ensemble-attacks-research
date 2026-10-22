# In-Class Work Session: Mandatory Brainstorming Questions

**Due on Canvas: Wednesday, Oct 14, 2026, 11:59 pm ET.** The submission version is `brainstorm-answers.pdf`, built from `brainstorm-answers.tex`. Each teammate submits their own copy: Q1 and Q4 are shared team answers ("we"), and Q2 and Q3 cover Mo's Shapley part ("I").

**Project:** Which Surrogates Matter? What Drives Success in Ensemble Transfer Attacks

**Team members:** Mo Liu, Connor Kilrain, Tom Heim

**Application area:** Computer Vision

---

**1. What task will you study? What dataset(s) and baseline model will you start with? Identify one primary trust axis and one secondary trust axis to address.**

Our team studies transfer-based black-box adversarial attacks on image classifiers, in which an attacker crafts adversarial examples on an ensemble of publicly available "surrogate" models and hopes they also fool an unseen target model; each of us takes a different angle on what makes some ensembles transfer better than others, and we will synthesize our findings. We will use standard image classification benchmarks (e.g., CIFAR-10, ImageNet) with a shared pool of publicly available pretrained classifiers, and a standard equal-weight ensemble attack as our common baseline. **Primary trust axis:** adversarial robustness; **secondary trust axis:** explainability.

**2. What is the proposed method you will implement, adapt, or change to address the problem?**

My part treats the surrogates as players in a cooperative game, where the payoff of any subset is how often an ensemble attack built from it fools held-out targets; each surrogate's Shapley value is then its average contribution, and pairwise interaction values show which surrogates are redundant and which are complementary. Since the number of subsets grows exponentially, I will compute these values exactly for a small pilot pool and estimate them by sampling for larger ones. I will then test whether explanation similarity between a surrogate and the target (e.g., how alike their saliency maps are) predicts Shapley value better than simple factors like architecture type or accuracy, and use the best predictor to pick a small, effective set of surrogates without rerunning the full analysis.

**3. What evaluation metric will you use, and what stress test or sanity check will you run?**

My main metric is the attack success rate on held-out targets, along with how well each predictor tracks the surrogates' Shapley values. To assess efficiency, I will measure how much of the full ensemble's success rate a small selected subset retains at a fraction of the compute; this builds on Shapley's efficiency axiom, under which the full ensemble's success (above the clean-image baseline) is fully distributed across the surrogates, so each Shapley value reads as that surrogate's share of the credit. As a stress test, I will evaluate on targets whose architecture type is absent from the surrogate pool; as a sanity check, I will confirm that a deliberately useless surrogate (e.g., an untrained model) receives near-zero credit, as the Shapley axioms require.

**4. What are the main data, compute, or timeline constraints? What is the biggest risk and your fallback plan?**

The main constraint is compute, since every part of the project needs many attack runs, so we will share one attack pipeline and model pool and pilot on a small dataset before scaling up. The biggest risk is that one simple factor, such as architecture type, explains most differences in transfer; our fallback is to report how the factors compare, which still shows which surrogate properties matter most. Each part also stands on its own if another does not pan out.

---

## For the team meeting (not part of the submission)

**How the work splits.** Each person still writes their own method and experiment section, as the course requires.
- **Shared by all three:** one attack pipeline, one pool of surrogate and target models, the same attack settings, and the same metric (attack success on held-out targets). Sharing these keeps results comparable and saves compute.
- **Mo (Shapley direction):** coalition attacks, Shapley and pairwise-interaction estimates, the explanation-similarity predictor, and surrogate selection.
- **Connor and Tom (other drivers of transfer):** to be decided. Architecture type is the leading candidate; other options are below.

**Candidate directions for Connor and Tom.** All of these work with off-the-shelf pretrained models, so no training is needed.
- **Architecture type and diversity:** CNN vs. ViT, and how mixed the ensemble is.
- **Training method:** standard vs. adversarially trained ("robust") surrogates. Prior work found that slightly robust surrogates make better attackers.
- **Training data and pretraining style:** ImageNet-only vs. larger datasets; supervised vs. self-supervised vs. image-and-caption (CLIP) models.
- **Ensemble size and combination method:** how many surrogates, and how their outputs are averaged and weighted.

**Optional bridge between directions.** Connor's and Tom's factors can be checked against Mo's Shapley values. For example: do cross-family or slightly robust surrogates earn more credit? This keeps each direction independent but gives the final report one storyline.

**Mo's working hypothesis (Shapley direction).** A surrogate's value to an ensemble attack depends more on how much it adds to the others than on its standalone strength:
- Same-family models will be redundant.
- Cross-family models (e.g., a CNN plus a ViT) will be synergistic.
- Surrogates whose explanations resemble the target's will carry the most value.

**Details to settle later, for the proposal (due ~Oct 21):**
- Specific models and dataset order.
- Attack budget.
- Stronger baselines. Candidates: SEAA (ICME '24) and AdaEA (ICCV '23).

**Decisions to confirm:**
1. ~~Fill in team names~~ Done.
2. Connor's and Tom's directions.
3. ~~Download SEAA~~ Done. The PDF is in this folder.

**How we differ from SEAA, the closest prior work.**
- **What it does.** SEAA reweights a fixed set of 4 CNN surrogates at every attack step. Its payoff is a one-step loss increase on one of its *own* surrogates, rotated in as a stand-in victim. That measures fit, not transfer.
- **What we do differently.** We use Shapley values as the *finding*: contribution to fooling *held-out* targets, across a pool that spans architecture families, plus pairwise interactions, subset selection and explanation-similarity predictors.
- **How we use it.** Cite SEAA as the closest work and use it as a baseline. Possible bonus: compare SEAA's internal weights with our held-out Shapley values.

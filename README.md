# Which Surrogates Matter? What Drives Success in Ensemble Transfer Attacks

CPSC 4710/5710 Trustworthy Deep Learning (Yale, Fall 2026) course project by Connor Kilrain and Mo Liu.

Transfer attacks craft adversarial examples on an ensemble of public "surrogate" models and hope they also fool an unseen target model. We share one attack pipeline (MI-FGSM on averaged logits, untargeted, L∞ ε = 16/255), model pool, and metric (fooling rate on held-out targets), and each study a different driver of transfer:

- **Direction A (Mo):** Shapley valuation of surrogates. Attack every subset of 8 surrogates (255 coalitions), score each on 6 held-out targets, and compute exact Shapley values and pairwise interactions.
- **Direction B (Connor):** architectural diversity, comparing same-family and mixed-family ensembles of equal size.

Dataset: NIPS 2017 Adversarial Learning Development Set (1,000 ImageNet-compatible images).

## Layout

| Path | Contents |
|---|---|
| `20261021_project-proposal/` | Brainstorm answers, pitch list, SEAA paper (closest prior work) |
| `20261021_project-proposal/proposal/` | Proposal source (`proposal_updated.tex`, `references.bib`, NeurIPS style), figures, and compiled PDF |
| `20261021_project-proposal/proposal/eda/` | EDA script and the dataset statistics quoted in the proposal |

## Deadlines

| Date | Deliverable |
|---|---|
| Oct 21 | Project proposal |
| Nov 13 | Project milestone |
| Dec 16 | Final report |

## Rebuilding the EDA figures

The dataset is not committed. Download the `dataset/` folder of [ZhengyuZhao/Targeted-Transfer](https://github.com/ZhengyuZhao/Targeted-Transfer) and PyTorch Hub's [`imagenet_classes.txt`](https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt), then run:

```bash
pip install numpy pandas matplotlib pillow
python eda/eda.py <dataset_dir> <imagenet_classes.txt> figures eda/dataset_stats.md
```

from `20261021_project-proposal/proposal/`.

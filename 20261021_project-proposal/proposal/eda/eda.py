"""Exploratory data analysis for the NIPS 2017 ImageNet-compatible dev set.

Usage:
    python -I eda.py <dataset_dir> <imagenet_classes.txt> <figures_dir> <stats_md>

<dataset_dir> holds images/*.png and images.csv (copy from
github.com/ZhengyuZhao/Targeted-Transfer, folder dataset/).
<imagenet_classes.txt> is one class name per line, ImageNet-1k order
(github.com/pytorch/hub, imagenet_classes.txt).
"""

import hashlib
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# ImageNet-1k index ranges (0-indexed): 0-397 are animals, 151-268 of which are dog breeds.
DOGS = range(151, 269)
ANIMALS = range(0, 398)


def coarse_group(idx):
    if idx in DOGS:
        return "Dog breeds"
    if idx in ANIMALS:
        return "Other animals"
    return "Objects, scenes, food"


def main(dataset_dir, classes_path, fig_dir, stats_path):
    dataset_dir, fig_dir, stats_path = Path(dataset_dir), Path(fig_dir), Path(stats_path)
    fig_dir.mkdir(parents=True, exist_ok=True)
    classes = Path(classes_path).read_text().splitlines()
    assert len(classes) == 1000, len(classes)

    df = pd.read_csv(dataset_dir / "images.csv")
    # Labels follow the 1001-class Inception convention (0 = background), so shift by one.
    df["cls"] = df["TrueLabel"] - 1
    df["name"] = df["cls"].map(lambda i: classes[i])
    df["group"] = df["cls"].map(coarse_group)

    sizes, modes, hashes = Counter(), Counter(), Counter()
    channel_sum = np.zeros(3)
    channel_sq = np.zeros(3)
    hist = np.zeros((3, 256))
    n_pixels = 0
    for image_id in df["ImageId"]:
        img = Image.open(dataset_dir / "images" / f"{image_id}.png")
        sizes[img.size] += 1
        modes[img.mode] += 1
        arr = np.asarray(img.convert("RGB"))
        hashes[hashlib.md5(arr.tobytes()).hexdigest()] += 1
        flat = arr.reshape(-1, 3).astype(np.float64) / 255.0
        channel_sum += flat.sum(0)
        channel_sq += (flat**2).sum(0)
        n_pixels += flat.shape[0]
        for c in range(3):
            hist[c] += np.bincount(arr[..., c].ravel(), minlength=256)
    mean = channel_sum / n_pixels
    std = np.sqrt(channel_sq / n_pixels - mean**2)

    per_class = df["cls"].value_counts()
    images_per_class = per_class.value_counts().sort_index()
    group_share = df["group"].value_counts(normalize=True)
    label_space_share = {
        "Dog breeds": len(DOGS) / 1000,
        "Other animals": (len(ANIMALS) - len(DOGS)) / 1000,
        "Objects, scenes, food": (1000 - len(ANIMALS)) / 1000,
    }
    saturated = (hist[:, 0].sum() + hist[:, 255].sum()) / hist.sum()
    duplicates = sum(v - 1 for v in hashes.values() if v > 1)
    licenses = df["License"].value_counts()
    flickr = df["URL"].str.contains("flickr").mean()

    # Figure 1: one row of samples cycling through the coarse groups.
    rng = np.random.default_rng(0)
    picks = []
    for group in ["Dog breeds", "Other animals", "Objects, scenes, food"]:
        ids = df[df["group"] == group].index.to_numpy()
        picks.extend(rng.choice(ids, size=4, replace=False))
    order = [picks[i] for i in (0, 4, 8, 1, 5, 9)]
    fig, axes = plt.subplots(1, 6, figsize=(5.5, 0.92))
    for ax, row_idx in zip(axes.ravel(), order):
        row = df.loc[row_idx]
        ax.imshow(Image.open(dataset_dir / "images" / f"{row['ImageId']}.png"))
        name = row["name"] if len(row["name"]) <= 18 else row["name"][:17] + "."
        ax.set_title(name, fontsize=6.5, pad=2)
        ax.axis("off")
    fig.tight_layout(pad=0.2, w_pad=0.2, h_pad=0.4)
    fig.savefig(fig_dir / "eda_samples.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(fig_dir / "eda_samples.png", dpi=150, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    # Figure 2: label coverage, category mix, pixel intensities.
    plt.rcParams.update({"font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7})
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 1.38))

    ax = axes[0]
    ax.bar(images_per_class.index, images_per_class.values, color="#4C72B0")
    ax.set_xlabel("Images per class")
    ax.set_ylabel("Number of classes")
    ax.set_title(f"(a) {per_class.size}/1,000 classes present")
    ax.set_xticks(images_per_class.index)

    ax = axes[1]
    groups = list(label_space_share)
    x = np.arange(len(groups))
    ax.bar(x - 0.2, [group_share.get(g, 0) * 100 for g in groups], 0.4, label="This dataset", color="#4C72B0")
    ax.bar(x + 0.2, [label_space_share[g] * 100 for g in groups], 0.4, label="ImageNet-1k labels", color="#BBBBBB")
    ax.set_xticks(x)
    ax.set_xticklabels(["Dogs", "Other\nanimals", "Objects,\nscenes"], fontsize=6)
    ax.set_ylabel("Share (%)")
    ax.set_title("(b) Category mix")
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")

    ax = axes[2]
    bins = np.arange(256) / 255.0
    for c, color, label in zip(range(3), ["#C44E52", "#55A868", "#4C72B0"], "RGB"):
        ax.plot(bins, hist[c] / hist[c].sum(), color=color, lw=0.9, label=f"{label} (mean {mean[c]:.2f})")
        ax.axvline(IMAGENET_MEAN[c], color=color, lw=0.6, ls="--")
    ax.set_xlabel("Pixel intensity")
    ax.set_ylabel("Fraction of pixels")
    ax.set_title("(c) Channel intensities")
    ax.legend(fontsize=5.5, frameon=True, framealpha=1, edgecolor="none", loc="upper center", bbox_to_anchor=(0.5, 0.97))
    ax.set_yticks([])
    ax.set_ylim(0, hist.max(1).max() / hist[0].sum() * 2.6)

    fig.tight_layout(pad=0.3, w_pad=1.2)
    fig.savefig(fig_dir / "eda_stats.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(fig_dir / "eda_stats.png", dpi=150, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    top = per_class.head(8)
    lines = [
        "# NIPS 2017 dev set: EDA numbers",
        "",
        f"- Images: {len(df)}; sizes: {dict(sizes)}; modes: {dict(modes)}",
        f"- TrueLabel range: {df['TrueLabel'].min()}-{df['TrueLabel'].max()} (1001-class convention; class = TrueLabel - 1)",
        f"- Distinct classes: {per_class.size} of 1000; max images per class: {per_class.max()}; "
        f"classes with exactly 1 image: {(per_class == 1).sum()}",
        f"- Images per class distribution: {images_per_class.to_dict()}",
        "- Coarse groups (dataset share vs label-space share): "
        + "; ".join(f"{g}: {group_share.get(g, 0):.1%} vs {label_space_share[g]:.1%}" for g in groups),
        f"- Distinct target classes (TargetClass column): {df['TargetClass'].nunique()}",
        f"- Channel mean (RGB): {np.round(mean, 3).tolist()} vs ImageNet {list(IMAGENET_MEAN)}",
        f"- Channel std (RGB): {np.round(std, 3).tolist()} vs ImageNet {list(IMAGENET_STD)}",
        f"- Exact duplicate images: {duplicates}",
        f"- Saturated channel values (exactly 0 or 255): {saturated:.1%}",
        f"- Flickr-sourced: {flickr:.1%}; licenses: {licenses.to_dict()}",
        "- Most frequent classes: " + ", ".join(f"{classes[i]} ({n})" for i, n in top.items()),
    ]
    stats_path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(*sys.argv[1:5])

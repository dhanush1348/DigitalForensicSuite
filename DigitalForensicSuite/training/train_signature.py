"""
Training script for Siamese ResNet18 on CEDAR dataset.

Run:
    python training/train_signature.py \\
        --data-dir datasets/signatures/cedar \\
        --epochs 30 --batch-size 32 --lr 1e-4

Quick sanity / CPU debug (tiny subset, 2 epochs):
    python training/train_signature.py --cpu-debug --epochs 2

Output checkpoint: models/signature/best_siamese.pth
"""

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from sklearn.metrics import roc_auc_score

# Make sure project root is importable regardless of CWD
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from preprocessing.signature_preprocessing import build_cedar_pairs, preprocess_signature
from models.signature.siamese_resnet import SiameseResNet18, ContrastiveLoss


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class CedarPairDataset(Dataset):
    """Loads CEDAR (img_a, img_b, label) pairs on-the-fly."""

    def __init__(self, pairs, debug_n: int | None = None):
        self.pairs = pairs[:debug_n] if debug_n else pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        path_a, path_b, label = self.pairs[idx]
        img_a = preprocess_signature(path_a)
        img_b = preprocess_signature(path_b)
        return img_a, img_b, torch.tensor(label, dtype=torch.long)


# ---------------------------------------------------------------------------
# Training helpers
# ---------------------------------------------------------------------------

def compute_metrics(sims: list[float], labels: list[int]):
    """Compute AUC and Equal Error Rate from similarity scores."""
    sims_arr   = np.array(sims)
    labels_arr = np.array(labels)

    try:
        auc = roc_auc_score(labels_arr, 1 - sims_arr)  # lower sim → forged
    except ValueError:
        auc = 0.0

    # EER: threshold where FAR ≈ FRR
    thresholds = np.linspace(0, 1, 200)
    best_eer = 1.0
    for t in thresholds:
        preds = (sims_arr < t).astype(int)
        far = np.mean(preds[labels_arr == 0])   # genuine pairs called forged
        frr = np.mean(1 - preds[labels_arr == 1])  # forged pairs called genuine
        eer = (far + frr) / 2
        if eer < best_eer:
            best_eer = eer

    return auc, best_eer


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def train(args):
    device = torch.device("cpu") if args.cpu_debug else (
        torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    )
    print(f"[Train] Device: {device}")

    # Build pairs
    pairs = build_cedar_pairs(args.data_dir)
    debug_n = 64 if args.cpu_debug else None

    # 80/20 train-val split
    n_val  = max(1, int(len(pairs) * 0.2))
    n_train = len(pairs) - n_val
    train_pairs, val_pairs = pairs[:n_train], pairs[n_train:]

    train_ds = CedarPairDataset(train_pairs, debug_n=debug_n)
    val_ds   = CedarPairDataset(val_pairs,   debug_n=debug_n // 4 if debug_n else None)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=0, pin_memory=False)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=0, pin_memory=False)

    print(f"[Train] {len(train_ds)} train pairs, {len(val_ds)} val pairs")

    # Model
    model     = SiameseResNet18(pretrained=not args.cpu_debug).to(device)
    criterion = ContrastiveLoss(margin=1.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # Output path
    ckpt_dir = ROOT / "models" / "signature"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt = ckpt_dir / "best_siamese.pth"

    best_auc = 0.0

    for epoch in range(1, args.epochs + 1):
        # ── Train ──────────────────────────────────────────────────────────
        model.train()
        train_loss = 0.0
        t0 = time.time()

        for img_a, img_b, label in train_loader:
            img_a, img_b, label = img_a.to(device), img_b.to(device), label.to(device)
            optimizer.zero_grad()
            sim, emb_a, emb_b = model(img_a, img_b)
            loss = criterion(emb_a, emb_b, label)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        scheduler.step()
        train_loss /= len(train_loader)

        # ── Validate ────────────────────────────────────────────────────────
        model.eval()
        all_sims, all_labels = [], []
        with torch.no_grad():
            for img_a, img_b, label in val_loader:
                img_a, img_b = img_a.to(device), img_b.to(device)
                sim, _, _ = model(img_a, img_b)
                all_sims.extend(sim.cpu().numpy().tolist())
                all_labels.extend(label.numpy().tolist())

        auc, eer = compute_metrics(all_sims, all_labels)
        elapsed = time.time() - t0

        print(
            f"Epoch {epoch:03d}/{args.epochs} | "
            f"Loss: {train_loss:.4f} | AUC: {auc:.4f} | EER: {eer:.4f} | "
            f"{elapsed:.1f}s"
        )

        if auc > best_auc:
            best_auc = auc
            torch.save({
                "epoch":       epoch,
                "state_dict":  model.state_dict(),
                "auc":         auc,
                "eer":         eer,
            }, best_ckpt)
            print(f"  [Saved] Best checkpoint -> {best_ckpt}")

    print(f"\n[Done] Best AUC: {best_auc:.4f}  checkpoint: {best_ckpt}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Siamese ResNet18 on CEDAR")
    parser.add_argument("--data-dir",   default="datasets/signatures/cedar",
                        help="Path to CEDAR root (contains full_org/ and full_forg/)")
    parser.add_argument("--epochs",     type=int,   default=30)
    parser.add_argument("--batch-size", type=int,   default=32)
    parser.add_argument("--lr",         type=float, default=1e-4)
    parser.add_argument("--cpu-debug",  action="store_true",
                        help="Use CPU + tiny data subset for quick integration test")
    args = parser.parse_args()
    train(args)

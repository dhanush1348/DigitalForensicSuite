"""
Training script for EfficientNet-B0 image forgery detector on CASIA v2.0.

Run:
    python training/train_image.py \\
        --data-dir datasets/images/CASIA2 \\
        --epochs 25 --batch-size 32 --lr 1e-4

Quick sanity / CPU debug:
    python training/train_image.py --cpu-debug --epochs 2

Output checkpoint: models/image_forgery/best_efficientnet.pth
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.metrics import roc_auc_score, classification_report
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from preprocessing.image_preprocessing import build_casia_dataset, generate_ela_image
from models.image_forgery.efficientnet_forgery import EfficientNetForgery


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

_train_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

_val_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


class CasiaDataset(Dataset):
    """Loads CASIA images through ELA pipeline."""

    def __init__(self, samples: list[tuple[str, int]], transform=None, debug_n: int | None = None):
        self.samples   = samples[:debug_n] if debug_n else samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            ela_img = generate_ela_image(path)
        except Exception:
            # Fallback: plain RGB if ELA fails (e.g., non-JPEG)
            ela_img = Image.open(path).convert("RGB").resize((224, 224))

        if self.transform:
            ela_img = self.transform(ela_img)

        return ela_img, torch.tensor(label, dtype=torch.long)


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train(args):
    device = torch.device("cpu") if args.cpu_debug else (
        torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    )
    print(f"[Train] Device: {device}")

    samples  = build_casia_dataset(args.data_dir)
    debug_n  = 64 if args.cpu_debug else None

    n_val    = max(1, int(len(samples) * 0.2))
    n_train  = len(samples) - n_val
    train_s, val_s = samples[:n_train], samples[n_train:]

    train_ds = CasiaDataset(train_s, transform=_train_tf, debug_n=debug_n)
    val_ds   = CasiaDataset(val_s,   transform=_val_tf,   debug_n=debug_n // 4 if debug_n else None)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=0)

    print(f"[Train] {len(train_ds)} train, {len(val_ds)} val images")

    model     = EfficientNetForgery(pretrained=not args.cpu_debug).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    ckpt_dir  = ROOT / "models" / "image_forgery"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt = Path(args.output)
    if not best_ckpt.is_absolute():
        best_ckpt = ROOT / best_ckpt
    best_ckpt.parent.mkdir(parents=True, exist_ok=True)

    best_auc  = 0.0

    for epoch in range(1, args.epochs + 1):
        # ── Train ──────────────────────────────────────────────────────────
        model.train()
        train_loss = 0.0
        t0 = time.time()

        total_train_batches = len(train_loader)
        for batch_idx, (imgs, labels) in enumerate(train_loader, start=1):
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(imgs)
            loss   = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            if batch_idx == 1 or batch_idx == total_train_batches or batch_idx % 10 == 0:
                progress = batch_idx / total_train_batches
                bar = "=" * int(progress * 24) + "." * (24 - int(progress * 24))
                print(f"\r[Train] Epoch {epoch:03d} [{bar}] {batch_idx}/{total_train_batches}", end="", flush=True)

        print()

        scheduler.step()
        train_loss /= len(train_loader)

        # ── Validate ────────────────────────────────────────────────────────
        model.eval()
        all_probs, all_labels = [], []
        with torch.no_grad():
            total_val_batches = len(val_loader)
            for batch_idx, (imgs, labels) in enumerate(val_loader, start=1):
                imgs = imgs.to(device)
                probs = F.softmax(model(imgs), dim=1)[:, 1]  # P(forged)
                all_probs.extend(probs.cpu().numpy().tolist())
                all_labels.extend(labels.numpy().tolist())
                if batch_idx == 1 or batch_idx == total_val_batches or batch_idx % 10 == 0:
                    progress = batch_idx / total_val_batches
                    bar = "=" * int(progress * 24) + "." * (24 - int(progress * 24))
                    print(f"\r[Val]   Epoch {epoch:03d} [{bar}] {batch_idx}/{total_val_batches}", end="", flush=True)

        print()

        try:
            auc = roc_auc_score(all_labels, all_probs)
        except ValueError:
            auc = 0.0

        preds_bin = [1 if p >= 0.5 else 0 for p in all_probs]
        acc = sum(p == l for p, l in zip(preds_bin, all_labels)) / len(all_labels)
        elapsed = time.time() - t0

        print(
            f"Epoch {epoch:03d}/{args.epochs} | "
            f"Loss: {train_loss:.4f} | AUC: {auc:.4f} | Acc: {acc:.4f} | "
            f"{elapsed:.1f}s"
        )

        if auc > best_auc:
            best_auc = auc
            torch.save({
                "epoch":      epoch,
                "state_dict": model.state_dict(),
                "auc":        auc,
                "acc":        acc,
            }, best_ckpt)
            print(f"  [Saved] Best checkpoint -> {best_ckpt}")

    print(f"\n[Done] Best AUC: {best_auc:.4f}  checkpoint: {best_ckpt}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train EfficientNet-B0 on CASIA v2.0")
    parser.add_argument("--data-dir",   default="datasets/images/CASIA2",
                        help="Path to CASIA2 directory (contains Au/ and Tp/)")
    parser.add_argument("--epochs",     type=int,   default=25)
    parser.add_argument("--batch-size", type=int,   default=32)
    parser.add_argument("--lr",         type=float, default=1e-4)
    parser.add_argument("--output",     default="models/image_forgery/best_efficientnet_casia_full.pth",
                        help="Checkpoint output path")
    parser.add_argument("--cpu-debug",  action="store_true",
                        help="Use CPU + tiny data subset for quick integration test")
    args = parser.parse_args()
    train(args)

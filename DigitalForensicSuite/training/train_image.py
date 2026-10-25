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
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from preprocessing.image_preprocessing import build_casia_dataset, generate_ela_image
from models.image_forgery.efficientnet_forgery import EfficientNetForgery
from evaluation.image_evaluation import calculate_metrics, write_evaluation_report


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

    sample_paths = [sample[0] for sample in samples]
    sample_labels = [sample[1] for sample in samples]
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        sample_paths,
        sample_labels,
        test_size=0.2,
        random_state=42,
        stratify=sample_labels,
    )
    train_s = list(zip(train_paths, train_labels))
    val_s = list(zip(val_paths, val_labels))

    train_ds = CasiaDataset(train_s, transform=_train_tf, debug_n=debug_n)
    val_ds   = CasiaDataset(val_s,   transform=_val_tf,   debug_n=debug_n // 4 if debug_n else None)

    loader_kwargs = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    if args.num_workers > 0:
        loader_kwargs["persistent_workers"] = True
    train_loader = DataLoader(train_ds, shuffle=True, **loader_kwargs)
    val_loader   = DataLoader(val_ds, shuffle=False, **loader_kwargs)

    print(f"[Train] {len(train_ds)} train, {len(val_ds)} val images")

    model     = EfficientNetForgery(pretrained=not args.cpu_debug).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    use_amp = args.amp and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    ckpt_dir  = ROOT / "models" / "image_forgery"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt = Path(args.output)
    if not best_ckpt.is_absolute():
        best_ckpt = ROOT / best_ckpt
    best_ckpt.parent.mkdir(parents=True, exist_ok=True)

    best_auc = 0.0
    best_metrics = None

    for epoch in range(1, args.epochs + 1):
        # ── Train ──────────────────────────────────────────────────────────
        model.train()
        train_loss = 0.0
        t0 = time.time()

        total_train_batches = len(train_loader)
        for batch_idx, (imgs, labels) in enumerate(train_loader, start=1):
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                logits = model(imgs)
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
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
                with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
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

        metrics = calculate_metrics(all_labels, all_probs)
        acc = metrics["accuracy"]
        elapsed = time.time() - t0

        print(
            f"Epoch {epoch:03d}/{args.epochs} | "
            f"Loss: {train_loss:.4f} | AUC: {auc:.4f} | Acc: {acc:.4f} | "
            f"{elapsed:.1f}s"
        )

        if auc > best_auc:
            best_auc = auc
            best_metrics = metrics
            torch.save({
                "epoch":      epoch,
                "state_dict": model.state_dict(),
                "auc":        auc,
                "acc":        acc,
                "metrics":    metrics,
            }, best_ckpt)
            print(f"  [Saved] Best checkpoint -> {best_ckpt}")

            report_dir = Path(args.report_dir)
            if not report_dir.is_absolute():
                report_dir = ROOT / report_dir
            report_paths = write_evaluation_report(metrics, report_dir)
            print(f"  [Report] Confusion matrix -> {report_paths['confusion_matrix']}")

    if best_metrics is None and all_labels:
        report_dir = Path(args.report_dir)
        if not report_dir.is_absolute():
            report_dir = ROOT / report_dir
        report_paths = write_evaluation_report(calculate_metrics(all_labels, all_probs), report_dir)
        print(f"  [Report] Confusion matrix -> {report_paths['confusion_matrix']}")

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
    parser.add_argument("--num-workers", type=int, default=2,
                        help="DataLoader worker processes; use 0 on constrained systems")
    parser.add_argument("--lr",         type=float, default=1e-4)
    parser.add_argument("--output",     default="models/image_forgery/best_efficientnet_casia_full.pth",
                        help="Checkpoint output path")
    parser.add_argument("--report-dir", default="reports/image_evaluation",
                        help="Directory for metrics, Markdown, and confusion-matrix reports")
    parser.add_argument("--cpu-debug",  action="store_true",
                        help="Use CPU + tiny data subset for quick integration test")
    parser.add_argument("--no-amp", dest="amp", action="store_false",
                        help="Disable CUDA mixed-precision training")
    parser.set_defaults(amp=True)
    args = parser.parse_args()
    train(args)

"""
Siamese ResNet18 for offline signature verification.

Architecture:
  - Shared ResNet18 encoder (ImageNet pretrained) — final FC removed
  - 512-d feature → 128-d L2-normalized embedding head
  - Contrastive loss during training
  - Cosine similarity at inference → similarity score ∈ [0, 1]

Usage:
    model = SiameseResNet18(pretrained=True)
    sim, emb_a, emb_b = model(img_a, img_b)   # forward returns similarity + embeddings
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models


class EmbeddingNet(nn.Module):
    """ResNet18 backbone with a 128-d L2-normalized embedding head."""

    def __init__(self, pretrained: bool = True):
        super().__init__()
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = models.resnet18(weights=weights)

        # Remove the original FC classifier — keep up to avgpool
        self.features = nn.Sequential(*list(backbone.children())[:-1])  # output: (B, 512, 1, 1)

        # Embedding projection head
        self.embed = nn.Sequential(
            nn.Flatten(),             # (B, 512)
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, H, W) normalized image tensor.
        Returns:
            L2-normalized embedding of shape (B, 128).
        """
        feat = self.features(x)   # (B, 512, 1, 1)
        emb  = self.embed(feat)   # (B, 128)
        return F.normalize(emb, p=2, dim=1)


class SiameseResNet18(nn.Module):
    """
    Siamese network that wraps a shared EmbeddingNet.

    forward() returns:
        similarity  — cosine similarity ∈ [0, 1]  (1 = identical)
        emb_a       — embedding of image A
        emb_b       — embedding of image B
    """

    def __init__(self, pretrained: bool = True):
        super().__init__()
        self.encoder = EmbeddingNet(pretrained=pretrained)

    def forward(
        self,
        img_a: torch.Tensor,
        img_b: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        emb_a = self.encoder(img_a)
        emb_b = self.encoder(img_b)
        # cosine similarity: output in [-1, 1], mapped to [0, 1] for convenience
        similarity = (F.cosine_similarity(emb_a, emb_b) + 1.0) / 2.0
        return similarity, emb_a, emb_b


# ---------------------------------------------------------------------------
# Contrastive Loss
# ---------------------------------------------------------------------------

class ContrastiveLoss(nn.Module):
    """
    Contrastive loss (Hadsell et al., 2006).

    label = 0 → genuine pair (similar) → minimize distance
    label = 1 → forged  pair (dissimilar) → maximize distance (up to margin)

    margin: Minimum distance penalty for impostor pairs (default 1.0).
    """

    def __init__(self, margin: float = 1.0):
        super().__init__()
        self.margin = margin

    def forward(
        self,
        emb_a: torch.Tensor,
        emb_b: torch.Tensor,
        label: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            emb_a, emb_b: L2-normalized embeddings of shape (B, D).
            label:        Tensor of shape (B,) with values 0 (genuine) or 1 (forged).
        Returns:
            Scalar loss.
        """
        dist = F.pairwise_distance(emb_a, emb_b, p=2)
        loss_genuine = (1 - label.float()) * dist.pow(2)
        loss_forged  = label.float() * F.relu(self.margin - dist).pow(2)
        return 0.5 * (loss_genuine + loss_forged).mean()

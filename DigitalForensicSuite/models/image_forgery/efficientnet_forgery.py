"""
EfficientNet-B0 image forgery detector.

Architecture:
  - EfficientNet-B0 backbone via `timm` (pretrained ImageNet)
  - Global average pool → 1280-d feature
  - Dropout(0.3) → Linear(1280, 2) classifier
  - Outputs logits for [AUTHENTIC=0, FORGED=1]

Usage:
    model = EfficientNetForgery(pretrained=True)
    logits = model(x)   # x: (B, 3, 224, 224)
    probs  = F.softmax(logits, dim=1)
"""

import timm
import torch
import torch.nn as nn


class EfficientNetForgery(nn.Module):
    """
    Binary image forgery classifier built on EfficientNet-B0.

    Args:
        pretrained: Whether to load ImageNet pretrained weights (default True).
        dropout:    Dropout probability before the final classifier (default 0.3).
    """

    def __init__(self, pretrained: bool = True, dropout: float = 0.3):
        super().__init__()

        # Load EfficientNet-B0 with pretrained weights, no built-in classifier
        self.backbone = timm.create_model(
            "efficientnet_b0",
            pretrained=pretrained,
            num_classes=0,       # remove head → returns 1280-d pooled feature
            global_pool="avg",
        )

        num_features = self.backbone.num_features  # 1280 for EfficientNet-B0

        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(num_features, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Image tensor of shape (B, 3, 224, 224), normalized to ImageNet stats.
        Returns:
            Logits of shape (B, 2): [logit_authentic, logit_forged].
        """
        features = self.backbone(x)      # (B, 1280)
        logits   = self.classifier(features)  # (B, 2)
        return logits

    def get_cam_target_layer(self) -> nn.Module:
        """Return the last convolutional block for Grad-CAM."""
        # EfficientNet-B0 in timm: backbone.blocks[-1] is the last MBConv block
        return self.backbone.blocks[-1]

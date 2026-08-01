"""
FinSight AI — Custom Lightweight Transformer Architecture
A from-scratch Transformer Encoder for financial sentiment classification.

Architecture:
    Input IDs → Token Embedding → Positional Encoding
    → [Multi-Head Self-Attention → Add&Norm → FFN → Add&Norm] × N layers
    → CLS Pooling → Dropout → Dense → Softmax → 3-class output

Returns attention weights from every layer for explainability.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class TokenEmbedding(nn.Module):
    """Learned token embeddings with scaling."""

    def __init__(self, vocab_size: int, embed_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.scale = math.sqrt(embed_dim)

    def forward(self, x):
        return self.embedding(x) * self.scale


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding (fixed, not learned)."""

    def __init__(self, embed_dim: int, max_len: int = 512, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, embed_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embed_dim, 2).float() * (-math.log(10000.0) / embed_dim)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, embed_dim)

        self.register_buffer("pe", pe)

    def forward(self, x):
        # x: (batch, seq_len, embed_dim)
        x = x + self.pe[:, : x.size(1), :]
        return self.dropout(x)


class MultiHeadSelfAttention(nn.Module):
    """
    Multi-Head Self-Attention mechanism.
    Returns both the output and attention weights for visualization.
    """

    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.query = nn.Linear(embed_dim, embed_dim)
        self.key = nn.Linear(embed_dim, embed_dim)
        self.value = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        self.attn_dropout = nn.Dropout(dropout)
        self.proj_dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape

        # Linear projections and reshape for multi-head
        Q = self.query(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.key(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.value(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        # Q, K, V: (batch, heads, seq_len, head_dim)

        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        # scores: (batch, heads, seq_len, seq_len)

        # Apply mask (for padding)
        if mask is not None:
            # mask: (batch, seq_len) → (batch, 1, 1, seq_len)
            mask = mask.unsqueeze(1).unsqueeze(2)
            scores = scores.masked_fill(mask == 0, float("-inf"))

        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.attn_dropout(attn_weights)

        # Weighted sum
        context = torch.matmul(attn_weights, V)
        # context: (batch, heads, seq_len, head_dim)

        # Concatenate heads
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_dim)

        # Final linear projection
        output = self.proj_dropout(self.out_proj(context))

        return output, attn_weights


class FeedForwardNetwork(nn.Module):
    """Position-wise Feed-Forward Network with GELU activation."""

    def __init__(self, embed_dim: int, ff_dim: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(embed_dim, ff_dim)
        self.linear2 = nn.Linear(ff_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()

    def forward(self, x):
        x = self.activation(self.linear1(x))
        x = self.dropout(x)
        x = self.linear2(x)
        return x


class TransformerEncoderBlock(nn.Module):
    """
    Single Transformer Encoder Block:
    Multi-Head Attention → Add & LayerNorm → FFN → Add & LayerNorm
    """

    def __init__(self, embed_dim: int, num_heads: int, ff_dim: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadSelfAttention(embed_dim, num_heads, dropout)
        self.ffn = FeedForwardNetwork(embed_dim, ff_dim, dropout)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Multi-head self attention with residual
        attn_output, attn_weights = self.attention(x, mask)
        x = self.norm1(x + self.dropout1(attn_output))

        # Feed-forward with residual
        ffn_output = self.ffn(x)
        x = self.norm2(x + self.dropout2(ffn_output))

        return x, attn_weights


class FinSightTransformer(nn.Module):
    """
    FinSight Custom Transformer Encoder for Financial Sentiment Classification.

    Architecture:
        Token Embedding → Positional Encoding
        → TransformerEncoderBlock × num_layers
        → CLS token pooling → Dropout → Classification head → 3-class output

    Returns:
        logits: (batch, num_classes)
        attention_weights: list of (batch, num_heads, seq_len, seq_len) per layer
    """

    def __init__(
        self,
        vocab_size: int = 15000,
        embed_dim: int = 128,
        num_heads: int = 4,
        num_layers: int = 3,
        ff_dim: int = 256,
        max_len: int = 256,
        num_classes: int = 3,
        dropout: float = 0.2,
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.ff_dim = ff_dim
        self.max_len = max_len
        self.num_classes = num_classes

        # Embedding layers
        self.token_embedding = TokenEmbedding(vocab_size, embed_dim)
        self.positional_encoding = PositionalEncoding(embed_dim, max_len, dropout)

        # Transformer encoder blocks
        self.encoder_blocks = nn.ModuleList(
            [
                TransformerEncoderBlock(embed_dim, num_heads, ff_dim, dropout)
                for _ in range(num_layers)
            ]
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, num_classes),
        )

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Xavier uniform initialization for linear layers."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.padding_idx is not None:
                    nn.init.zeros_(module.weight[module.padding_idx])

    def forward(self, input_ids, attention_mask=None):
        """
        Forward pass.

        Args:
            input_ids: (batch, seq_len) token IDs
            attention_mask: (batch, seq_len) 1=real token, 0=padding

        Returns:
            logits: (batch, num_classes)
            all_attention_weights: list[Tensor(batch, heads, seq, seq)] per layer
        """
        # Embedding + positional encoding
        x = self.token_embedding(input_ids)
        x = self.positional_encoding(x)

        # Pass through encoder blocks, collect attention weights
        all_attention_weights = []
        for encoder_block in self.encoder_blocks:
            x, attn_weights = encoder_block(x, attention_mask)
            all_attention_weights.append(attn_weights)

        # CLS token pooling (first token)
        cls_output = x[:, 0, :]

        # Classification
        logits = self.classifier(cls_output)

        return logits, all_attention_weights

    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def get_architecture_info(self) -> dict:
        """Return architecture metadata."""
        return {
            "model_name": "FinSight Transformer v1",
            "architecture": "Custom Transformer Encoder",
            "vocab_size": self.vocab_size,
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "num_layers": self.num_layers,
            "ff_dim": self.ff_dim,
            "max_seq_len": self.max_len,
            "num_classes": self.num_classes,
            "total_parameters": self.count_parameters(),
            "components": [
                {
                    "name": "Token Embedding",
                    "type": "nn.Embedding",
                    "input_shape": f"(batch, {self.max_len})",
                    "output_shape": f"(batch, {self.max_len}, {self.embed_dim})",
                    "parameters": self.vocab_size * self.embed_dim,
                    "description": "Maps each token ID to a dense vector representation of financial language.",
                },
                {
                    "name": "Positional Encoding",
                    "type": "Sinusoidal",
                    "input_shape": f"(batch, {self.max_len}, {self.embed_dim})",
                    "output_shape": f"(batch, {self.max_len}, {self.embed_dim})",
                    "parameters": 0,
                    "description": "Injects word position information using sine and cosine functions so the model knows word order.",
                },
                {
                    "name": f"Transformer Encoder × {self.num_layers}",
                    "type": "TransformerEncoderBlock",
                    "input_shape": f"(batch, {self.max_len}, {self.embed_dim})",
                    "output_shape": f"(batch, {self.max_len}, {self.embed_dim})",
                    "parameters": sum(
                        p.numel()
                        for block in self.encoder_blocks
                        for p in block.parameters()
                    ),
                    "description": "Each block applies multi-head self-attention followed by a feed-forward network with residual connections and layer normalization.",
                    "sub_components": [
                        {
                            "name": "Multi-Head Self-Attention",
                            "type": "Scaled Dot-Product",
                            "heads": self.num_heads,
                            "head_dim": self.embed_dim // self.num_heads,
                            "description": "Allows the model to identify relationships between different words regardless of their position within the sentence.",
                        },
                        {
                            "name": "Add & Layer Normalization",
                            "type": "LayerNorm",
                            "description": "Residual connection preserves original information while normalization stabilizes training.",
                        },
                        {
                            "name": "Feed-Forward Network",
                            "type": "2-layer MLP + GELU",
                            "hidden_dim": self.ff_dim,
                            "description": "Applies non-linear transformations to each token representation independently.",
                        },
                    ],
                },
                {
                    "name": "CLS Pooling",
                    "type": "Token Selection",
                    "input_shape": f"(batch, {self.max_len}, {self.embed_dim})",
                    "output_shape": f"(batch, {self.embed_dim})",
                    "parameters": 0,
                    "description": "Extracts the [CLS] token representation which captures the global context of the entire input.",
                },
                {
                    "name": "Classification Head",
                    "type": "MLP",
                    "input_shape": f"(batch, {self.embed_dim})",
                    "output_shape": f"(batch, {self.num_classes})",
                    "parameters": sum(
                        p.numel() for p in self.classifier.parameters()
                    ),
                    "description": "Maps the contextual representation to sentiment class probabilities through dense layers with dropout.",
                },
            ],
        }

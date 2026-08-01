"""
FinSight AI — Custom Word-Level Tokenizer
Builds vocabulary from training corpus, encodes/decodes text to token IDs.
"""

import json
import re
from collections import Counter
from typing import List, Optional


class FinSightTokenizer:
    """Custom word-level tokenizer for financial text."""

    PAD_TOKEN = "[PAD]"
    UNK_TOKEN = "[UNK]"
    CLS_TOKEN = "[CLS]"

    PAD_ID = 0
    UNK_ID = 1
    CLS_ID = 2

    SPECIAL_TOKENS = [PAD_TOKEN, UNK_TOKEN, CLS_TOKEN]

    def __init__(self, vocab_size: int = 15000, max_len: int = 256):
        self.vocab_size = vocab_size
        self.max_len = max_len
        self.word2id = {}
        self.id2word = {}
        self._initialized = False

    def build_vocab(self, texts: List[str]) -> None:
        """Build vocabulary from a list of texts."""
        counter = Counter()
        for text in texts:
            tokens = self._tokenize(text)
            counter.update(tokens)

        # Reserve slots for special tokens
        num_regular = self.vocab_size - len(self.SPECIAL_TOKENS)

        # Take most common words
        most_common = counter.most_common(num_regular)

        # Build mappings
        self.word2id = {}
        for i, token in enumerate(self.SPECIAL_TOKENS):
            self.word2id[token] = i

        for i, (word, _count) in enumerate(most_common):
            self.word2id[word] = i + len(self.SPECIAL_TOKENS)

        self.id2word = {v: k for k, v in self.word2id.items()}
        self._initialized = True

    def encode(
        self,
        text: str,
        max_len: Optional[int] = None,
        add_cls: bool = True,
        padding: bool = True,
    ) -> dict:
        """Encode text to token IDs with attention mask."""
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized. Call build_vocab() or load() first.")

        max_len = max_len or self.max_len
        tokens = self._tokenize(text)

        # Add CLS token
        if add_cls:
            tokens = [self.CLS_TOKEN] + tokens

        # Truncate
        if len(tokens) > max_len:
            tokens = tokens[:max_len]

        # Convert to IDs
        token_ids = [self.word2id.get(t, self.UNK_ID) for t in tokens]

        # Create attention mask (1 for real tokens, 0 for padding)
        attention_mask = [1] * len(token_ids)

        # Pad
        if padding:
            pad_len = max_len - len(token_ids)
            token_ids = token_ids + [self.PAD_ID] * pad_len
            attention_mask = attention_mask + [0] * pad_len

        return {
            "input_ids": token_ids,
            "attention_mask": attention_mask,
            "tokens": tokens,
            "num_tokens": sum(attention_mask),
        }

    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs back to text."""
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized.")

        words = []
        for tid in token_ids:
            word = self.id2word.get(tid, self.UNK_TOKEN)
            if word not in self.SPECIAL_TOKENS:
                words.append(word)
        return " ".join(words)

    def get_tokens(self, text: str) -> List[str]:
        """Get token list for a text (no encoding)."""
        return self._tokenize(text)

    def save(self, path: str) -> None:
        """Save tokenizer vocabulary to JSON."""
        data = {
            "vocab_size": self.vocab_size,
            "max_len": self.max_len,
            "word2id": self.word2id,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> None:
        """Load tokenizer vocabulary from JSON."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab_size = data["vocab_size"]
        self.max_len = data["max_len"]
        self.word2id = data["word2id"]
        self.id2word = {int(v): k for k, v in self.word2id.items()}
        self._initialized = True

    @property
    def actual_vocab_size(self) -> int:
        """Return the actual number of tokens in vocabulary."""
        return len(self.word2id)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Basic word tokenization."""
        if not text:
            return []
        text = text.lower().strip()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens

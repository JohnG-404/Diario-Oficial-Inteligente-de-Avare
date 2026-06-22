"""
src/model.py — Modelo de Classificação Textual

Arquitetura: Embedding → média dos vetores → camadas lineares → softmax
Referência: Kim (2014) simplificado para base pequena
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ClassificadorTexto(nn.Module):
    """
    Classificador textual baseado em média de embeddings (Bag-of-Words Neural).

    Fluxo:
        tokens (batch, seq_len) → embeddings (batch, seq_len, emb_dim)
        → média (batch, emb_dim) → Linear → ReLU → Dropout → Linear → logits

    Parâmetros
    ----------
    vocab_size : int
        Tamanho do vocabulário (incluindo <PAD>=0 e <UNK>=1)
    emb_dim : int
        Dimensão dos vetores de embedding (default: 64)
    hidden_dim : int
        Dimensão da camada oculta (default: 128)
    num_classes : int
        Número de classes de saída (default: 6)
    dropout : float
        Taxa de dropout para regularização (default: 0.3)
    pad_idx : int
        Índice do token de padding — não contribui para a média (default: 0)
    """

    def __init__(
        self,
        vocab_size: int,
        emb_dim: int = 64,
        hidden_dim: int = 128,
        num_classes: int = 6,
        dropout: float = 0.3,
        pad_idx: int = 0,
    ):
        super().__init__()

        # Camada de embedding: pad_idx=0 → gradiente zero no padding
        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=emb_dim,
            padding_idx=pad_idx,
        )

        # Classificador MLP (dois estágios)
        self.fc1 = nn.Linear(emb_dim, hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Parâmetros
        ----------
        x : torch.Tensor  shape (batch, seq_len)
            Sequências de índices de tokens

        Retorna
        -------
        torch.Tensor  shape (batch, num_classes)
            Logits não normalizados para cada classe
        """
        # (batch, seq_len) → (batch, seq_len, emb_dim)
        emb = self.embedding(x)

        # Máscara para ignorar o padding (índice 0) na média
        # (batch, seq_len) → (batch, seq_len, 1)
        mask = (x != 0).float().unsqueeze(-1)
        soma = (emb * mask).sum(dim=1)           # (batch, emb_dim)
        contagem = mask.sum(dim=1).clamp(min=1)  # evita divisão por zero
        media = soma / contagem                   # (batch, emb_dim)

        # MLP: Linear → ReLU → Dropout → Linear
        out = F.relu(self.fc1(media))
        out = self.dropout(out)
        logits = self.fc2(out)

        return logits


def criar_modelo(vocab_size: int, num_classes: int = 6, **kwargs) -> ClassificadorTexto:
    """
    Factory function para criar o modelo com hiperparâmetros padrão.

    Exemplo
    -------
    >>> modelo = criar_modelo(vocab_size=250, num_classes=6)
    >>> print(sum(p.numel() for p in modelo.parameters()))
    """
    return ClassificadorTexto(
        vocab_size=vocab_size,
        num_classes=num_classes,
        emb_dim=kwargs.get("emb_dim", 64),
        hidden_dim=kwargs.get("hidden_dim", 128),
        dropout=kwargs.get("dropout", 0.3),
    )


def contar_parametros(modelo: nn.Module) -> int:
    """Retorna o total de parâmetros treináveis do modelo."""
    return sum(p.numel() for p in modelo.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Teste rápido de sanidade
    VOCAB_SIZE = 250
    BATCH_SIZE = 8
    SEQ_LEN = 60
    NUM_CLASSES = 6

    modelo = criar_modelo(VOCAB_SIZE, NUM_CLASSES)
    print(f"Parâmetros treináveis: {contar_parametros(modelo):,}")

    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    logits = modelo(x)

    print(f"Entrada:  {x.shape}")
    print(f"Saída:    {logits.shape}")
    assert logits.shape == (BATCH_SIZE, NUM_CLASSES), "Shape incorreto!"
    print("✅ Teste de sanidade passou.")

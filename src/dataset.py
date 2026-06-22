"""
src/dataset.py — Dataset PyTorch para o Diário Oficial de Avaré

Compatível com torch.utils.data.DataLoader.
Constrói vocabulário, codifica rótulos e converte textos em tensores.
"""

import re
import json
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from sklearn.model_selection import train_test_split

# ── Stopwords em português ────────────────────────────────────────────────────
STOPWORDS = {
    'de','da','do','das','dos','e','o','a','os','as','para','no','na','nos',
    'nas','que','em','um','uma','com','por','ao','aos','se','sua','seu',
    'pela','pelo','fica','art','nº','nr','ns','rs','ou','mais','mas','ser',
    'ter','foi','tem','são','este','esta','estes','estas','esse','essa',
    'esses','essas','todo','toda','todos','todas','não','também','já','sobre',
    'entre','até','muito','apenas','só','bem','ainda','quando','como','pelo',
    'pelas','pelos','num','numa','neste','nesta','deste','desta',
}

MAX_LEN = 60  # cobre 100% dos textos da base (P95 = 50 tokens)


def tokenizar(texto: str) -> list:
    """Converte texto em lista de tokens limpos (lowercase, sem pontuação)."""
    if not isinstance(texto, str):
        return []
    texto = texto.lower()
    texto = re.sub(r'[^a-zà-ú\s]', ' ', texto)
    tokens = texto.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


class DiarioDataset(Dataset):
    """
    Dataset PyTorch para classificação de atos do Diário Oficial.

    Parâmetros
    ----------
    textos : list[str]
        Textos limpos dos atos
    rotulos : list[int]
        Índices inteiros das classes
    vocab : dict[str, int]
        Dicionário token → índice
    max_len : int
        Comprimento máximo da sequência (padding / truncamento)
    """

    def __init__(self, textos, rotulos, vocab, max_len=MAX_LEN):
        self.textos = textos
        self.rotulos = rotulos
        self.vocab = vocab
        self.max_len = max_len

    def __len__(self):
        return len(self.textos)

    def __getitem__(self, idx):
        tokens = tokenizar(self.textos[idx])

        # Converte tokens em índices (1 = <UNK> para tokens fora do vocab)
        indices = [self.vocab.get(t, 1) for t in tokens]

        # Trunca ou faz padding com 0 (<PAD>)
        if len(indices) > self.max_len:
            indices = indices[: self.max_len]
        else:
            indices += [0] * (self.max_len - len(indices))

        x = torch.tensor(indices, dtype=torch.long)
        y = torch.tensor(self.rotulos[idx], dtype=torch.long)
        return x, y


def carregar_datasets(
    csv_path: str = "data/processed/amostra_rotulada.csv",
    vocab_path: str = "data/processed/vocab.json",
    label_map_path: str = "data/processed/label_map.json",
    batch_size: int = 8,
    test_size: float = 0.2,
    random_state: int = 42,
):
    """
    Carrega os arquivos gerados na Etapa 3 e retorna DataLoaders prontos para treino.

    Retorna
    -------
    treino_loader, teste_loader, vocab, label_map, id2label
    """
    df = pd.read_csv(csv_path)

    with open(vocab_path, encoding="utf-8") as f:
        vocab = json.load(f)
    with open(label_map_path, encoding="utf-8") as f:
        label_map = json.load(f)

    id2label = {v: k for k, v in label_map.items()}
    df["rotulo_id"] = df["rotulo"].map(label_map)

    treino_df, teste_df = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=df["rotulo_id"]
    )

    treino_ds = DiarioDataset(
        treino_df["texto"].tolist(), treino_df["rotulo_id"].tolist(), vocab
    )
    teste_ds = DiarioDataset(
        teste_df["texto"].tolist(), teste_df["rotulo_id"].tolist(), vocab
    )

    treino_loader = DataLoader(treino_ds, batch_size=batch_size, shuffle=True)
    teste_loader = DataLoader(teste_ds, batch_size=batch_size, shuffle=False)

    return treino_loader, teste_loader, vocab, label_map, id2label

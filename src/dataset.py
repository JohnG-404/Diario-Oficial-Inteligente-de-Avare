# src/dataset.py
# Classe DiarioDataset compatível com PyTorch
# Etapa 3 — NLP e Preparação para PyTorch

import re
import json
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import pandas as pd

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

MAX_LEN = 60   # cobre o percentil 95 da base (50 tokens) com margem


def tokenizar(texto: str) -> list[str]:
    """
    Transforma texto em lista de tokens:
    1. Converte para minúsculas
    2. Remove pontuação e números (mantém letras acentuadas)
    3. Remove stopwords e tokens de 1 caractere
    """
    if not isinstance(texto, str):
        return []
    texto = texto.lower()
    texto = re.sub(r'[^a-zà-ú\s]', ' ', texto)
    tokens = texto.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def codificar_texto(texto: str, vocab: dict, max_len: int = MAX_LEN) -> list[int]:
    """
    Converte um texto em lista de inteiros usando o vocabulário.
    - Tokens desconhecidos recebem índice 1 (<UNK>)
    - Padding com 0 (<PAD>) até max_len
    - Trunca em max_len se necessário
    """
    tokens = tokenizar(texto)
    ids = [vocab.get(t, 1) for t in tokens]   # 1 = <UNK>
    ids = ids[:max_len]                         # trunca
    ids = ids + [0] * (max_len - len(ids))      # padding com <PAD> = 0
    return ids


class DiarioDataset(Dataset):
    """
    Dataset das publicações do Diário Oficial de Avaré.

    Cada item retorna:
        x: tensor LongTensor de shape (max_len,) — sequência de IDs de tokens
        y: tensor LongTensor escalar — ID do rótulo (classe)

    Exemplo de uso:
        ds = DiarioDataset(df, vocab, label2id)
        loader = DataLoader(ds, batch_size=8, shuffle=True)
        x, y = next(iter(loader))
        # x.shape == [8, 60]  |  y.shape == [8]
    """

    def __init__(self, dataframe: pd.DataFrame, vocab: dict,
                 label2id: dict, max_len: int = MAX_LEN):
        self.textos   = dataframe['texto'].tolist()
        self.rotulos  = dataframe['rotulo'].tolist()
        self.vocab    = vocab
        self.label2id = label2id
        self.max_len  = max_len

    def __len__(self) -> int:
        return len(self.textos)

    def __getitem__(self, idx: int):
        ids       = codificar_texto(self.textos[idx], self.vocab, self.max_len)
        rotulo_id = self.label2id[self.rotulos[idx]]
        x = torch.tensor(ids, dtype=torch.long)
        y = torch.tensor(rotulo_id, dtype=torch.long)
        return x, y


def carregar_datasets(
    csv_path:        str  = 'data/processed/amostra_rotulada.csv',
    vocab_path:      str  = 'data/processed/vocab.json',
    label_map_path:  str  = 'data/processed/label_map.json',
    batch_size:      int  = 8,
    max_len:         int  = MAX_LEN,
    test_size:       float = 0.2,
    random_state:    int  = 42,
):
    """
    Carrega todos os artefatos e retorna DataLoaders prontos para treino.

    Retorna:
        treino_loader, teste_loader, vocab, label2id, id2label
    """
    df = pd.read_csv(csv_path)

    with open(vocab_path, encoding='utf-8') as f:
        vocab = json.load(f)

    with open(label_map_path, encoding='utf-8') as f:
        label2id = json.load(f)

    id2label = {v: k for k, v in label2id.items()}

    df['rotulo_id'] = df['rotulo'].map(label2id)

    treino_df, teste_df = train_test_split(
        df, test_size=test_size, random_state=random_state,
        stratify=df['rotulo_id']
    )

    treino_ds = DiarioDataset(treino_df, vocab, label2id, max_len)
    teste_ds  = DiarioDataset(teste_df,  vocab, label2id, max_len)

    treino_loader = DataLoader(treino_ds, batch_size=batch_size, shuffle=True)
    teste_loader  = DataLoader(teste_ds,  batch_size=batch_size, shuffle=False)

    print(f'Treino: {len(treino_ds)} amostras | Teste: {len(teste_ds)} amostras')
    print(f'Vocab: {len(vocab)} tokens | Classes: {len(label2id)} | max_len: {max_len}')

    return treino_loader, teste_loader, vocab, label2id, id2label


# ── Teste rápido ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    treino_loader, teste_loader, vocab, label2id, id2label = carregar_datasets()

    x_lote, y_lote = next(iter(treino_loader))

    print(f'\nFormato X: {x_lote.shape}')   # [8, 60]
    print(f'Formato y: {y_lote.shape}')      # [8]
    print(f'Rótulos do lote: {[id2label[i.item()] for i in y_lote]}')
    print(f'Valores X (linha 0): {x_lote[0].tolist()}')
    print('\n✅ Dataset funcionando corretamente!')

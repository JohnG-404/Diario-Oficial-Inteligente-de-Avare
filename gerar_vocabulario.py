# gerar_vocabulario.py
# Lê amostra_rotulada.csv e gera:
#   data/processed/vocab.json      → dicionário token → índice
#   data/processed/label_map.json  → dicionário rótulo → inteiro
#
# Execute da raiz do projeto: python gerar_vocabulario.py
# Pré-requisito: data/processed/amostra_rotulada.csv deve existir (gerado na Etapa 2)

import re
import json
import pandas as pd
from pathlib import Path
from collections import Counter
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

def tokenizar(texto: str) -> list:
    if not isinstance(texto, str):
        return []
    texto = texto.lower()
    texto = re.sub(r'[^a-zà-ú\s]', ' ', texto)
    tokens = texto.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

# ── Carrega a base rotulada ───────────────────────────────────────────────────
csv_path = Path('data/processed/amostra_rotulada.csv')
if not csv_path.exists():
    raise FileNotFoundError(f'Arquivo não encontrado: {csv_path}\nExecute primeiro a Etapa 2.')

df = pd.read_csv(csv_path)
print(f'{len(df)} registros carregados')
print(f'Classes: {sorted(df["rotulo"].unique())}')

# ── Divide treino/teste ANTES de construir o vocabulário ─────────────────────
# IMPORTANTE: o vocabulário é construído APENAS com os textos de treino.
# Se usarmos todos os dados, o modelo "vê" tokens do teste antes de treinar
# (data leakage), o que inflaria artificialmente a avaliação.

classes = sorted(df['rotulo'].unique())
label2id = {c: i for i, c in enumerate(classes)}
df['rotulo_id'] = df['rotulo'].map(label2id)

treino_df, teste_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df['rotulo_id']
)
print(f'\nSplit — Treino: {len(treino_df)} | Teste: {len(teste_df)}')

# ── Constrói o vocabulário com os textos de TREINO ───────────────────────────
contador = Counter()
for texto in treino_df['texto']:
    contador.update(tokenizar(texto))

# Tokens especiais obrigatórios
vocab = {'<PAD>': 0, '<UNK>': 1}

# Adiciona tokens com frequência >= 2 (elimina hapax legomena — ruído)
for token, freq in contador.most_common():
    if freq >= 2:
        vocab[token] = len(vocab)

print(f'Vocabulário: {len(vocab)} tokens (freq >= 2)')

# ── Salva os artefatos ────────────────────────────────────────────────────────
output_dir = Path('data/processed')
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'vocab.json', 'w', encoding='utf-8') as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

with open(output_dir / 'label_map.json', 'w', encoding='utf-8') as f:
    json.dump(label2id, f, ensure_ascii=False, indent=2)

print(f'\nvocab.json salvo      → {len(vocab)} tokens')
print(f'label_map.json salvo  → {label2id}')


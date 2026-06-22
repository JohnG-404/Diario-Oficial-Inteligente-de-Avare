"""
src/inferencia.py — Função de Inferência

Carrega o modelo treinado e classifica textos novos.

Uso programático:
    from src.inferencia import carregar_pipeline, classificar

    pipeline = carregar_pipeline()
    resultado = classificar("DECRETO Nº 8.742, DE 14 DE MAIO DE 2026...", pipeline)
    print(resultado)

Uso via linha de comando:
    python src/inferencia.py "DECRETO Nº 8.742..."
"""

import sys
import json
import re
import torch
from pathlib import Path

from src.model import criar_modelo

# Stopwords (mesma lista usada no dataset.py para consistência)
STOPWORDS = {
    'de','da','do','das','dos','e','o','a','os','as','para','no','na','nos',
    'nas','que','em','um','uma','com','por','ao','aos','se','sua','seu',
    'pela','pelo','fica','art','nº','nr','ns','rs','ou','mais','mas','ser',
    'ter','foi','tem','são','este','esta','estes','estas','esse','essa',
    'esses','essas','todo','toda','todos','todas','não','também','já','sobre',
    'entre','até','muito','apenas','só','bem','ainda','quando','como','pelo',
    'pelas','pelos','num','numa','neste','nesta','deste','desta',
}

MAX_LEN = 60

# Nomes amigáveis das classes para exibição na UI
NOMES_CLASSES = {
    "decreto": "📜 Decreto Municipal",
    "lei": "⚖️ Lei Municipal",
    "portaria": "📋 Portaria Administrativa",
}


def tokenizar(texto: str) -> list:
    """Mesma tokenização do dataset.py."""
    if not isinstance(texto, str):
        return []
    texto = texto.lower()
    texto = re.sub(r'[^a-zà-ú\s]', ' ', texto)
    tokens = texto.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def carregar_pipeline(
    modelo_path: str = "models/modelo.pt",
    vocab_path: str = "data/processed/vocab.json",
    device: str = None,
) -> dict:
    """
    Carrega o modelo treinado, vocabulário e mapeamentos em um pipeline reutilizável.

    Retorna
    -------
    dict com chaves: modelo, vocab, id2label, device
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device)

    # ── Carrega vocab ────────────────────────────────────────────
    with open(vocab_path, encoding="utf-8") as f:
        vocab = json.load(f)

    # ── Carrega checkpoint ───────────────────────────────────────
    checkpoint = torch.load(modelo_path, map_location=device)
    label_map  = checkpoint["label_map"]
    id2label   = checkpoint["id2label"]
    # id2label pode vir com chaves como strings (JSON) — normaliza para int
    id2label   = {int(k): v for k, v in id2label.items()}

    vocab_size  = checkpoint["vocab_size"]
    num_classes = checkpoint["num_classes"]

    modelo = criar_modelo(vocab_size=vocab_size, num_classes=num_classes)
    modelo.load_state_dict(checkpoint["model_state_dict"])
    modelo.to(device)
    modelo.eval()

    return {
    "modelo": modelo,
    "vocab": vocab,
    "label_map": label_map,
    "id2label": id2label,
    "device": device,
}


def classificar(texto: str, pipeline: dict, top_k: int = 3) -> dict:
    """
    Classifica um texto e retorna as probabilidades por classe.

    Parâmetros
    ----------
    texto : str
        Texto do ato a classificar (pode ser o texto completo ou trecho)
    pipeline : dict
        Retorno de `carregar_pipeline()`
    top_k : int
        Quantas classes retornar no ranking (default: 3)

    Retorna
    -------
    dict com:
        classe      — rótulo da classe mais provável
        nome        — nome amigável da classe
        confianca   — probabilidade da classe mais provável (0–1)
        ranking     — lista de (rótulo, nome, probabilidade) top_k
    """
    vocab   = pipeline["vocab"]
    modelo  = pipeline["modelo"]
    id2label = pipeline["id2label"]
    device  = pipeline["device"]

    # Tokenização e codificação
    tokens  = tokenizar(texto)
    indices = [vocab.get(t, 1) for t in tokens]  # 1 = <UNK>

    # Padding / truncamento
    if len(indices) > MAX_LEN:
        indices = indices[:MAX_LEN]
    else:
        indices += [0] * (MAX_LEN - len(indices))

    x = torch.tensor([indices], dtype=torch.long).to(device)  # (1, MAX_LEN)

    with torch.no_grad():
        logits = modelo(x)                          # (1, num_classes)
        probs  = torch.softmax(logits, dim=1)[0]    # (num_classes,)

    # Ordena por probabilidade decrescente
    ranking_ids = probs.argsort(descending=True).tolist()
    ranking = [
        {
            "classe":    id2label[i],
            "nome":      NOMES_CLASSES.get(id2label[i], id2label[i]),
            "confianca": round(probs[i].item(), 4),
        }
        for i in ranking_ids[:top_k]
    ]

    melhor = ranking[0]
    return {
        "classe":    melhor["classe"],
        "nome":      melhor["nome"],
        "confianca": melhor["confianca"],
        "ranking":   ranking,
        "tokens_usados": len([t for t in tokens if vocab.get(t, 1) != 1]),
        "tokens_total":  len(tokens),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/inferencia.py \"<texto do ato>\"")
        sys.exit(1)

    texto_entrada = " ".join(sys.argv[1:])

    print("Carregando pipeline...")
    pipe = carregar_pipeline()
    print("Pipeline carregado.\n")

    resultado = classificar(texto_entrada, pipe)

    print(f"Classe predita : {resultado['nome']}")
    print(f"Confiança      : {resultado['confianca'] * 100:.1f}%")
    print(f"Tokens no vocab: {resultado['tokens_usados']}/{resultado['tokens_total']}")
    print("\nTop-3 classes:")
    for i, r in enumerate(resultado["ranking"], 1):
        barra = "█" * int(r["confianca"] * 20)
        print(f"  {i}. {r['nome']:<35} {barra} {r['confianca']*100:.1f}%")

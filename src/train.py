"""
src/train.py — Treino, Avaliação e Geração de Artefatos

Uso:
    python src/train.py

Gera:
    models/modelo.pt            — pesos do modelo treinado
    data/processed/curva_loss.png
    data/processed/matriz_confusao.png
"""

import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
import matplotlib.pyplot as plt
import seaborn as sns

from model import criar_modelo, contar_parametros
from dataset import carregar_datasets

# ── Reprodutibilidade ─────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# ── Hiperparâmetros ───────────────────────────────────────────────────────────
EPOCAS = 20
LR = 1e-3
BATCH_SIZE = 8
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def calcular_class_weights(label_map: dict, df_path: str) -> torch.Tensor:
    """
    Calcula pesos inversamente proporcionais à frequência de cada classe.
    Compensa o desbalanceamento moderado (razão máx/mín ≈ 2,4x).
    """
    df = pd.read_csv(df_path)
    contagens = df["rotulo"].value_counts()
    total = len(df)
    num_classes = len(label_map)

    pesos = torch.zeros(num_classes)
    for rotulo, idx in label_map.items():
        freq = contagens.get(rotulo, 1)
        pesos[idx] = total / (num_classes * freq)

    return pesos


def treinar_epoca(modelo, loader, criterio, otimizador, device):
    modelo.train()
    loss_total = 0.0
    acertos = 0
    total = 0

    for x, y in loader:
        x, y = x.to(device), y.to(device)
        otimizador.zero_grad()
        logits = modelo(x)
        loss = criterio(logits, y)
        loss.backward()
        otimizador.step()

        loss_total += loss.item() * y.size(0)
        acertos += (logits.argmax(dim=1) == y).sum().item()
        total += y.size(0)

    return loss_total / total, acertos / total


def avaliar(modelo, loader, criterio, device):
    modelo.eval()
    loss_total = 0.0
    acertos = 0
    total = 0

    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = modelo(x)
            loss = criterio(logits, y)
            loss_total += loss.item() * y.size(0)
            acertos += (logits.argmax(dim=1) == y).sum().item()
            total += y.size(0)

    return loss_total / total, acertos / total


def plotar_curvas(historico: dict, output_dir: Path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Loss
    axes[0].plot(historico["treino_loss"], label="Treino", color="steelblue")
    axes[0].plot(historico["teste_loss"], label="Teste", color="coral", linestyle="--")
    axes[0].set_title("Curva de Loss")
    axes[0].set_xlabel("Época")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Acurácia
    axes[1].plot(historico["treino_acc"], label="Treino", color="steelblue")
    axes[1].plot(historico["teste_acc"], label="Teste", color="coral", linestyle="--")
    axes[1].set_title("Curva de Acurácia")
    axes[1].set_xlabel("Época")
    axes[1].set_ylabel("Acurácia")
    axes[1].set_ylim(0, 1.05)
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    caminho = output_dir / "curva_loss.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"📈 Curvas salvas em {caminho}")


def plotar_confusao(y_true, y_pred, id2label: dict, output_dir: Path):
    classes = [id2label[i] for i in range(len(id2label))]
    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
        ax=ax,
    )
    ax.set_title("Matriz de Confusão — Conjunto de Teste")
    ax.set_xlabel("Predito")
    ax.set_ylabel("Real")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    caminho = output_dir / "matriz_confusao.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"📊 Matriz de confusão salva em {caminho}")


def coletar_predicoes(modelo, loader, device):
    modelo.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            logits = modelo(x)
            preds = logits.argmax(dim=1).cpu().tolist()
            y_true.extend(y.tolist())
            y_pred.extend(preds)
    return y_true, y_pred


def main():
    print(f"Dispositivo: {DEVICE}")
    print("=" * 60)

    # ── Carrega dados ─────────────────────────────────────────────
    treino_loader, teste_loader, vocab, label_map, id2label = carregar_datasets(
        batch_size=BATCH_SIZE
    )
    print(f"Vocab size:   {len(vocab)}")
    print(f"Num classes:  {len(label_map)}")
    print(f"Label map:    {label_map}")

    # ── Cria modelo ───────────────────────────────────────────────
    modelo = criar_modelo(vocab_size=len(vocab), num_classes=len(label_map)).to(DEVICE)
    print(f"Parâmetros:   {contar_parametros(modelo):,}")

    # ── Class weights para desbalanceamento ───────────────────────
    pesos = calcular_class_weights(
        label_map, "data/processed/amostra_rotulada.csv"
    ).to(DEVICE)
    criterio = nn.CrossEntropyLoss(weight=pesos)
    otimizador = torch.optim.Adam(modelo.parameters(), lr=LR)

    # Scheduler: reduz LR em platôs
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        otimizador, patience=5, factor=0.5, verbose=True
    )

    # ── Loop de treino ────────────────────────────────────────────
    historico = {
        "treino_loss": [], "treino_acc": [],
        "teste_loss": [],  "teste_acc": [],
    }

    melhor_acc = 0.0
    Path("models").mkdir(exist_ok=True)

    print("\nÉpoca | Treino Loss | Treino Acc | Teste Loss | Teste Acc")
    print("-" * 62)

    for epoca in range(1, EPOCAS + 1):
        tl, ta = treinar_epoca(modelo, treino_loader, criterio, otimizador, DEVICE)
        vl, va = avaliar(modelo, teste_loader, criterio, DEVICE)

        scheduler.step(vl)

        historico["treino_loss"].append(tl)
        historico["treino_acc"].append(ta)
        historico["teste_loss"].append(vl)
        historico["teste_acc"].append(va)

        print(f"  {epoca:3d}  |   {tl:.4f}    |   {ta:.4f}   |   {vl:.4f}   |   {va:.4f}")

        # Salva o melhor modelo (checkpoint)
        if va >= melhor_acc:
            melhor_acc = va
            torch.save(
                {
                    "epoch": epoca,
                    "model_state_dict": modelo.state_dict(),
                    "optimizer_state_dict": otimizador.state_dict(),
                    "vocab_size": len(vocab),
                    "num_classes": len(label_map),
                    "label_map": label_map,
                    "id2label": id2label,
                },
                "models/modelo.pt",
            )

    print(f"\n✅ Melhor acurácia no teste: {melhor_acc:.4f}")
    print("💾 Modelo salvo em models/modelo.pt")

    # ── Avaliação final ───────────────────────────────────────────
    # Carrega o melhor checkpoint
    checkpoint = torch.load("models/modelo.pt", map_location=DEVICE)
    modelo.load_state_dict(checkpoint["model_state_dict"])

    y_true, y_pred = coletar_predicoes(modelo, teste_loader, DEVICE)
    classes = [id2label[i] for i in range(len(id2label))]

    print("\n" + "=" * 60)
    print("RELATÓRIO DE CLASSIFICAÇÃO (conjunto de teste)")
    print("=" * 60)
    print(classification_report(y_true, y_pred, target_names=classes))

    acc = accuracy_score(y_true, y_pred)
    print(f"Acurácia geral: {acc:.4f} ({int(acc * len(y_true))}/{len(y_true)})")

    # ── Análise de erros ──────────────────────────────────────────
    print("\nANÁLISE DE ERROS:")
    for real, pred in zip(y_true, y_pred):
        if real != pred:
            print(f"  Real: {id2label[real]:<22} → Predito: {id2label[pred]}")

    # ── Artefatos visuais ─────────────────────────────────────────
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    plotar_curvas(historico, output_dir)
    plotar_confusao(y_true, y_pred, id2label, output_dir)

    # Salva histórico como JSON para o relatório
    with open(output_dir / "historico_treino.json", "w") as f:
        json.dump(historico, f, indent=2)

    print("\n✅ Etapa 4 concluída.")


if __name__ == "__main__":
    main()

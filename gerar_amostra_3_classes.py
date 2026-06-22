import pandas as pd

df = pd.read_csv("data/processed/base_textual.csv")

mapeamento = {
    "Leis": "lei",
    "Decretos": "decreto",
    "Portarias": "portaria"
}

df = df[df["tipo_ato"].isin(mapeamento.keys())].copy()

df["rotulo"] = df["tipo_ato"].map(mapeamento)

# balancear para não ficar 2291 x 241
amostras = []

for classe in ["lei", "decreto", "portaria"]:
    subset = df[df["rotulo"] == classe]

    n = min(200, len(subset))

    amostras.append(
        subset.sample(
            n=n,
            random_state=42
        )
    )

resultado = pd.concat(amostras)

resultado.to_csv(
    "data/processed/amostra_rotulada.csv",
    index=False,
    encoding="utf-8-sig"
)

print(resultado["rotulo"].value_counts())
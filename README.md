# Diário Oficial Inteligente de Avaré

**Projeto de Redes Neurais e IA Aplicada — NLP, PyTorch e classificação textual de atos oficiais**

> Transformando publicações do Diário Oficial do Município de Avaré/SP em uma base textual estruturada e em um classificador neural funcional.

---

## Grupo

| Nome | Turma |
|------|-------|
| Gabriel Bianco Sanches | 9º termo |
| Gabriel Santana dos Santos | 9º termo |
| Guilherme Monteiro da Luz | 9º termo |
| João Gabriel Pereira Cardozo | 9º termo |
| João Gabriel Godoy Pereira | 9º termo |
| Lucas Nakamura Rodrigues | 9º termo |
| Lucas Vaz Barbosa | 9º termo |
| Pedro Lucas Campos | 7º termo |

**Repositório:** https://github.com/JohnG-404/Diario-Oficial-Inteligente-de-Avare

---

## Visão Geral

O projeto aplica uma pipeline completa de dados e redes neurais ao Diário Oficial de Avaré:

1. exploração e coleta automatizada de publicações;
2. extração e limpeza dos textos;
3. tokenização, vocabulário e preparação para PyTorch;
4. treinamento, avaliação e disponibilização de uma interface web.

Após a análise exploratória, o classificador foi ajustado para trabalhar com **3 classes principais** do corpus coletado:

- `decreto`
- `lei`
- `portaria`

A decisão foi tomada porque essas categorias possuem grande volume de documentos na base, permitindo treinamento mais estável e avaliação mais confiável do que a versão inicial com seis classes muito desbalanceadas.

---

## Resultados da Versão Atual

| Item | Resultado |
|------|----------:|
| Base textual total | 3883 publicações |
| Textos válidos | 3862 publicações |
| Amostra rotulada | 600 registros |
| Classes | 3 |
| Distribuição | 200 decretos, 200 leis, 200 portarias |
| Treino/Teste | 480 / 120 |
| Vocabulário | 17512 tokens |
| Parâmetros treináveis | 1.129.475 |
| Acurácia no teste | **85,83%** |

### Métricas por classe

| Classe | Precision | Recall | F1-score | Suporte |
|--------|----------:|-------:|---------:|--------:|
| decreto | 0.89 | 0.78 | 0.83 | 40 |
| lei | 0.79 | 0.95 | 0.86 | 40 |
| portaria | 0.92 | 0.85 | 0.88 | 40 |
| **macro avg** | **0.87** | **0.86** | **0.86** | **120** |

---

## Estrutura do Repositório

```text
diario-avare-nlp/
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   ├── base_textual.csv
│   │   ├── amostra_rotulada.csv        # 600 registros, 200 por classe
│   │   ├── vocab.json                  # 17.512 tokens
│   │   ├── label_map.json              # {'decreto': 0, 'lei': 1, 'portaria': 2}
│   │   ├── historico_treino.json
│   │   ├── curva_loss.png
│   │   └── matriz_confusao.png
│   └── diario_avare.csv
│
├── docs/
│   ├── dicionario_campos.md
│   ├── relatorio_etapa1.md
│   ├── relatorio_etapa2.md
│   ├── relatorio_etapa3.md
│   └── relatorio_etapa4.md
│
├── models/
│   └── modelo.pt
│
├── notebooks/
│   ├── 01_exploracao_site.ipynb
│   ├── 02_limpeza_textos.ipynb
│   ├── 03_analise_exploratoria.ipynb
│   └── 04_treinamento_avaliacao.ipynb
│
├── src/
│   ├── scraper.py
│   ├── extract_text.py
│   ├── preprocess.py
│   ├── dataset.py
│   ├── model.py
│   ├── train.py
│   └── inferencia.py
│
├── gerar_amostra_3_classes.py
├── gerar_vocabulario.py
├── app.py
├── requirements.txt
└── README.md
```

---

## Como Rodar

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Gerar a amostra rotulada de 3 classes

```bash
python gerar_amostra_3_classes.py
```

Resultado esperado:

```text
decreto     200
lei         200
portaria    200
```

### 4. Gerar vocabulário e mapa de classes

```bash
python gerar_vocabulario.py
```

Resultado esperado:

```text
600 registros carregados
Classes: ['decreto', 'lei', 'portaria']
Split — Treino: 480 | Teste: 120
Vocabulário: 17512 tokens
label_map.json salvo → {'decreto': 0, 'lei': 1, 'portaria': 2}
```

### 5. Treinar o modelo

```bash
python src/train.py
```

### 6. Rodar a interface web

```bash
python app.py
```

Acesse:

```text
http://localhost:5000
```

---

## Interface Web

A interface Flask permite colar um texto do Diário Oficial e obter a classificação automática.

Funcionalidades:

- campo de texto livre;
- exemplos rápidos de Lei, Decreto e Portaria;
- classe predita com nome amigável;
- confiança da previsão;
- ranking top-3 de probabilidades;
- endpoint `/health` para diagnóstico;
- endpoint `/classificar` para uso programático.

---

## Inferência via Linha de Comando

```bash
python src/inferencia.py "DECRETO Nº 8.742, DE 14 DE MAIO DE 2026. O PREFEITO MUNICIPAL DECRETA..."
```

Saída esperada:

```text
Classe predita : 📜 Decreto Municipal
Confiança      : 84.4%
Tokens no vocab: 24/24
```

---

## Arquitetura do Modelo

```text
Tokens (batch, 60)
      ↓
nn.Embedding [vocab_size × 64]
      ↓
Média mascarada, ignorando <PAD>
      ↓
nn.Linear 64 → 128 + ReLU + Dropout(0.3)
      ↓
nn.Linear 128 → 3
      ↓
Logits → softmax → 3 probabilidades
```

| Hiperparâmetro | Valor |
|----------------|------:|
| Embedding dim | 64 |
| Hidden dim | 128 |
| Dropout | 0.3 |
| Épocas | 20 |
| Batch size | 8 |
| Otimizador | Adam |
| Learning rate | 0.001 |
| Loss | CrossEntropyLoss |
| Parâmetros treináveis | 1.129.475 |

---

## Justificativa da Redução para 3 Classes

A versão inicial considerava seis classes, mas a análise da base mostrou forte desbalanceamento e baixo volume em algumas categorias. Como o objetivo da disciplina é demonstrar a pipeline de redes neurais de ponta a ponta, foi adotada uma versão com três classes amplamente representadas no corpus: Lei, Decreto e Portaria.

Essa decisão melhorou a qualidade dos dados, aumentou a amostra rotulada para 600 documentos e permitiu uma avaliação estatisticamente mais consistente.

---

## Nota sobre Coleta

O servidor `imprensaoficialmunicipal.com.br` pode bloquear requisições vindas de IPs de datacenters por WAF. Para coleta e extração, recomenda-se executar os scripts em rede doméstica ou institucional.

---

## Referências

- Site do Diário Oficial de Avaré: https://imprensaoficialmunicipal.com.br/avare
- Projeto de referência: https://github.com/netoferraz/acordaos-tcu
- PyTorch: https://pytorch.org/docs/stable/
- Flask: https://flask.palletsprojects.com/
- scikit-learn: https://scikit-learn.org/stable/

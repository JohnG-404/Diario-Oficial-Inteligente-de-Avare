# Relatório da Etapa 3 — NLP e Preparação para PyTorch

**Projeto:** Diário Oficial Inteligente de Avaré  
**Semana:** 3 de 4

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

## 1. Resumo Executivo

Nesta etapa, a base textual foi transformada em dados numéricos compatíveis com o PyTorch. O processo incluiu análise exploratória, tokenização, construção de vocabulário, codificação de rótulos e implementação do `DiarioDataset`.

A versão atual utiliza **600 documentos rotulados** e balanceados entre três classes: `decreto`, `lei` e `portaria`.

---

## 2. Distribuição das Classes

| Classe | Registros | Percentual |
|--------|----------:|-----------:|
| decreto | 200 | 33,3% |
| lei | 200 | 33,3% |
| portaria | 200 | 33,3% |
| **Total** | **600** | **100%** |

A distribuição balanceada evita que o modelo favoreça uma classe dominante e torna as métricas de avaliação mais confiáveis.

---

## 3. Divisão Treino/Teste

A base foi dividida com `train_test_split`, mantendo estratificação por classe.

| Split | Registros | Percentual |
|-------|----------:|-----------:|
| Treino | 480 | 80% |
| Teste | 120 | 20% |

Cada classe possui 160 exemplos no treino e 40 exemplos no teste.

---

## 4. Pré-processamento NLP

A tokenização aplicada na Etapa 3 segue as mesmas regras usadas posteriormente no `dataset.py` e no `inferencia.py`.

| Transformação | Decisão |
|---------------|---------|
| Converter para minúsculas | sim |
| Remover pontuação e números isolados | sim |
| Manter acentos | sim |
| Remover stopwords | sim |
| Remover tokens de 1 caractere | sim |
| Stemming/lematização | não |

A manutenção dos acentos preserva características do português, enquanto a remoção de stopwords reduz o ruído para um modelo simples baseado em média de embeddings.

---

## 5. Vocabulário

O vocabulário foi construído a partir dos textos de treino, evitando vazamento de dados do teste.

| Parâmetro | Valor |
|-----------|------:|
| Frequência mínima | 2 |
| Tokens especiais | `<PAD>=0`, `<UNK>=1` |
| Tamanho final | 17512 tokens |
| Fonte | textos do conjunto de treino |

O uso de frequência mínima igual a 2 remove tokens raros e erros de extração, reduzindo ruído no treinamento.

---

## 6. Codificação dos Rótulos

```python
{'decreto': 0, 'lei': 1, 'portaria': 2}
```

Esse mapeamento foi salvo em `data/processed/label_map.json` e é usado tanto no treinamento quanto na inferência.

---

## 7. Dataset PyTorch

A classe `DiarioDataset` converte cada texto em uma sequência de índices de tamanho fixo.

```text
Texto original
    ↓
tokenizar()
    ↓
lookup no vocab
    ↓
padding/truncamento para MAX_LEN
    ↓
tensor torch.long
```

Formato esperado do lote:

```text
X: [batch_size, MAX_LEN]
y: [batch_size]
```

---

## 8. Artefatos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `data/processed/amostra_rotulada.csv` | 600 registros balanceados |
| `data/processed/vocab.json` | vocabulário com 17512 tokens |
| `data/processed/label_map.json` | mapeamento das 3 classes |
| `src/dataset.py` | Dataset PyTorch e DataLoaders |
| `notebooks/03_analise_exploratoria.ipynb` | análise exploratória atualizada |
| `docs/distribuicao_classes.png` | distribuição das classes |
| `docs/termos_por_classe.png` | termos frequentes por classe |

---

## 9. Justificativa Técnica

A versão inicial com seis classes apresentava baixo volume e desbalanceamento em categorias como `edital_concurso`, `portaria` e `licitacao_contrato`. Para fins didáticos e para garantir um treinamento neural mais confiável, a base foi reformulada para três classes com forte representatividade no corpus.

Essa decisão preserva o objetivo da disciplina: demonstrar a construção de uma pipeline completa de classificação textual com redes neurais.

---

## 10. Próximos Passos

A Etapa 4 utiliza os DataLoaders gerados aqui para treinar o modelo `EmbeddingAvg + MLP`, avaliar as métricas no conjunto de teste e disponibilizar o classificador via interface Flask.

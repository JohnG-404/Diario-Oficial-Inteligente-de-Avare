# Relatório da Etapa 3 — NLP e Preparação para PyTorch

**Projeto:** Diário Oficial Inteligente de Avaré  
**Semana:** 3 de 4

---

## 1. Resumo Executivo

Nesta etapa transformamos a base textual da Etapa 2 em **tensores prontos para uma rede neural**. As decisões técnicas estão documentadas abaixo com justificativas baseadas nos dados observados na EDA.

---

## 2. Atividade 1 — Análise Exploratória (EDA)

### 2.1 Distribuição das classes

| Classe | Registros | % |
|--------|-----------|---|
| decreto | 12 | 28,6% |
| licitacao_contrato | 8 | 19,0% |
| portaria | 7 | 16,7% |
| ato_pessoal | 5 | 11,9% |
| edital_concurso | 5 | 11,9% |
| contas_publicas | 5 | 11,9% |
| **Total** | **42** | 100% |

**Diagnóstico:** desbalanceamento moderado (razão máx/mín = 2,4x). Não é crítico para o tamanho da base, mas na Etapa 4 usaremos `class_weight` no `CrossEntropyLoss` para compensar.

### 2.2 Comprimento dos textos (tokens após stopwords)

| Estatística | Valor |
|-------------|-------|
| Mínimo | 31 |
| Média | 40,5 |
| Mediana | 40,0 |
| Máximo | 56 |
| Percentil 95 | 50 |

**Decisão sobre MAX_LEN:** adotamos **60 tokens**, que cobre 100% da base com folga. Um valor menor (ex: 40) truncaria ~25% dos textos; um valor maior (ex: 128) desperdiçaria memória sem ganho real.

### 2.3 Termos mais frequentes

Os termos mais frequentes por classe confirmam que o vocabulário tem poder discriminativo:

- **licitacao_contrato:** *pregão, eletrônico, cnpj, ltda, contrato, valor, objeto*
- **contas_publicas:** *receita, despesa, orçamentária, correntes, total, lei, dezembro*
- **edital_concurso:** *concurso, vagas, cargo, pontos, classificação, edital*
- **decreto:** *decreta, prefeito, regulamenta, avaré, municipal*
- **ato_pessoal:** *nomear, exonerar, cargo, comissão, servidor, portaria*
- **portaria:** *resolve, considerando, secretário, designa, comissão*

---

## 3. Atividade 2 — Decisões de Pré-processamento NLP

### Transformações aplicadas

| Transformação | Decisão | Justificativa |
|---------------|---------|---------------|
| Minúsculas | ✅ Aplicado | 'Decreto' e 'decreto' são o mesmo conceito |
| Remove pontuação/números | ✅ Aplicado | Não carregam informação semântica para classificação |
| Remove acentos | ❌ Não aplicado | Preserva informação do português (ex: 'saúde' ≠ 'saude') |
| Remove stopwords | ✅ Aplicado | Reduz vocabulário sem perda semântica relevante |
| Stemming/lematização | ❌ Não aplicado | Aumentaria complexidade sem ganho claro na base atual |
| Mínimo de 2 caracteres | ✅ Aplicado | Elimina artefatos de extração |

### Stopwords removidas

Foram removidas 45 stopwords do português, incluindo preposições (*de, da, do, para*), artigos (*o, a, os, as*) e verbos auxiliares comuns (*ser, ter, foi*). A lista completa está em `src/dataset.py`.

---

## 4. Atividade 3 — Vocabulário

### Parâmetros

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| Construído com | Apenas treino (33 docs) | Evitar data leakage |
| Frequência mínima | 2 ocorrências | Corta tokens raros que seriam ruído |
| Tamanho final | **248 tokens** | Adequado para a escala da base |
| `<PAD>` | índice 0 | Padding de sequências curtas |
| `<UNK>` | índice 1 | Tokens ausentes no vocabulário |

### Por que construir o vocabulário só com treino?

Se construirmos o vocabulário com todos os dados (treino + teste), o modelo terá índices para tokens que "nunca viu" durante o treino, mas que existem no teste — isso é **data leakage**. Na prática, isso infla artificialmente o desempenho avaliado, pois o vocabulário vaza informação do teste para o modelo.

---

## 5. Atividade 4 — Codificação dos Rótulos

```
{'ato_pessoal': 0, 'contas_publicas': 1, 'decreto': 2,
 'edital_concurso': 3, 'licitacao_contrato': 4, 'portaria': 5}
```

Classes ordenadas alfabeticamente para garantir reprodutibilidade. O mapeamento inverso (`id2label`) permite recuperar o nome da classe a partir do índice predito pelo modelo.

---

## 6. Atividade 5 — Dataset PyTorch

### Resultado do teste

```
Formato X: torch.Size([8, 60])   ✅  [batch_size, MAX_LEN]
Formato y: torch.Size([8])       ✅  [batch_size]
Valores X: inteiros em [0, 247]  ✅  dentro do vocabulário
```

### Divisão treino/teste

| Split | Registros | % |
|-------|-----------|---|
| Treino | 33 | 79% |
| Teste | 9 | 21% |

Estratificação por classe (`stratify=df['rotulo_id']`) garante proporção equivalente em ambos os splits, essencial com base pequena.

---

## 7. Atividade 6 — Comparação com PyTorch-NLP

| Aspecto | Nossa implementação | PyTorch-NLP |
|---------|--------------------|-|
| Vocabulário | `dict {token: int}` | `WhitespaceEncoder` automático |
| `<PAD>` / `<UNK>` | Explícitos, índices 0 e 1 | Automáticos |
| Padding | Manual (`+ [0] * n`) | Via `encoder.encode()` |
| Encoder de rótulos | `dict` manual | `LabelEncoder` automático |
| Transparência | Total — cada passo visível | Caixa cinza |
| Flexibilidade | Alta | Limitada à API da lib |

**Conclusão:** a implementação manual é superior para fins didáticos — cada decisão é explícita e compreensível. Para projetos em produção, ferramentas como `PyTorch-NLP` ou `HuggingFace Tokenizers` economizam tempo com suporte a vocabulários maiores e tokenizadores mais sofisticados (BPE, WordPiece).

---

## 8. Artefatos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `data/processed/vocab.json` | Vocabulário: 248 tokens (token → índice) |
| `data/processed/label_map.json` | Mapeamento de rótulos: 6 classes (rótulo → inteiro) |
| `src/dataset.py` | Classe `DiarioDataset` + `carregar_datasets()` |
| `notebooks/03_analise_exploratoria.ipynb` | EDA completa com gráficos |
| `docs/distribuicao_classes.png` | Gráfico de distribuição das classes |
| `docs/comprimento_textos.png` | Histograma e boxplot do comprimento |
| `docs/termos_por_classe.png` | Top 10 tokens por classe |

---

## 9. Próximos Passos (Etapa 4)

- Usar `treino_loader` e `teste_loader` em `src/train.py`
- Treinar modelo `TextCNN` (kernel sizes 2, 3, 4 — rápido e eficaz para textos curtos)
- Avaliar com acurácia, F1-score por classe e matriz de confusão
- Investigar se as classes com menos exemplos (`ato_pessoal`, `edital_concurso`, `contas_publicas`) se beneficiam de `class_weight`

---

*Relatório da Etapa 3 — Semana 3*

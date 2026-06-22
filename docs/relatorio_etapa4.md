# Relatório da Etapa 4 — Treinamento, Avaliação e Interface

**Projeto:** Diário Oficial Inteligente de Avaré  
**Semana:** 4 de 4

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

Nesta etapa final foi treinado e avaliado um classificador textual neural para publicações do Diário Oficial de Avaré. A arquitetura adotada foi **EmbeddingAvg + MLP**, composta por embeddings, média mascarada dos vetores e camadas lineares.

A versão final do projeto utiliza **600 documentos rotulados**, distribuídos igualmente entre as classes `decreto`, `lei` e `portaria`. O modelo atingiu **85,83% de acurácia** no conjunto de teste com 120 exemplos.

---

## 2. Arquitetura do Modelo

```text
Entrada: sequência de tokens (batch, 60)
         ↓
nn.Embedding vocab_size × 64
         ↓
Média mascarada, ignorando <PAD>=0
         ↓
nn.Linear 64 → 128
         ↓
ReLU
         ↓
Dropout(0.3)
         ↓
nn.Linear 128 → 3
         ↓
Logits → softmax → probabilidades
```

### Hiperparâmetros

| Parâmetro | Valor |
|-----------|------:|
| Embedding dim | 64 |
| Hidden dim | 128 |
| Dropout | 0.3 |
| MAX_LEN | 60 |
| Batch size | 8 |
| Épocas | 20 |
| Learning rate | 0.001 |
| Otimizador | Adam |
| Scheduler | ReduceLROnPlateau |
| Parâmetros treináveis | 1.129.475 |

---

## 3. Configuração do Treinamento

A base foi dividida em 480 exemplos de treino e 120 exemplos de teste. Como a amostra foi balanceada, cada classe ficou com 160 exemplos no treino e 40 no teste.

| Split | Decreto | Lei | Portaria | Total |
|-------|--------:|----:|---------:|------:|
| Treino | 160 | 160 | 160 | 480 |
| Teste | 40 | 40 | 40 | 120 |

---

## 4. Evolução do Treinamento

O treinamento apresentou queda consistente da perda e estabilização da acurácia de teste entre as épocas finais.

| Época | Treino Loss | Treino Acc | Teste Loss | Teste Acc |
|------:|------------:|-----------:|-----------:|----------:|
| 1 | 1.0587 | 0.4771 | 0.9986 | 0.6750 |
| 5 | 0.3593 | 0.8688 | 0.4621 | 0.8250 |
| 10 | 0.1936 | 0.9167 | 0.4371 | 0.8333 |
| 15 | 0.1348 | 0.9354 | 0.4618 | 0.8417 |
| 20 | 0.1230 | 0.9396 | 0.4844 | 0.8500 |

A melhor acurácia observada no teste foi **0.8583**, equivalente a **85,83%**.

---

## 5. Métricas de Avaliação

```text
Acurácia geral: 0.8583 (103/120)
```

| Classe | Precision | Recall | F1-score | Suporte |
|--------|----------:|-------:|---------:|--------:|
| decreto | 0.89 | 0.78 | 0.83 | 40 |
| lei | 0.79 | 0.95 | 0.86 | 40 |
| portaria | 0.92 | 0.85 | 0.88 | 40 |
| **accuracy** |  |  | **0.86** | **120** |
| **macro avg** | **0.87** | **0.86** | **0.86** | **120** |
| **weighted avg** | **0.87** | **0.86** | **0.86** | **120** |

---

## 6. Análise de Erros

Foram observados 17 erros em 120 exemplos de teste. As principais confusões ocorreram entre **decretos e leis**, o que é esperado porque ambos usam linguagem jurídico-administrativa semelhante, com termos como `Art.`, `Lei`, `Município`, `Prefeito`, `Avaré`, datas e referências normativas.

Também ocorreram algumas confusões envolvendo portarias, especialmente em textos com estrutura formal parecida com decretos ou leis.

---

## 7. Inferência

A função `classificar()` recebe um texto qualquer e retorna:

- classe prevista;
- nome amigável da classe;
- confiança da previsão;
- ranking top-3;
- quantidade de tokens reconhecidos no vocabulário.

Exemplo:

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

## 8. Interface Web

A interface foi implementada em Flask com Bootstrap 5 e JavaScript simples.

Funcionalidades:

| Funcionalidade | Descrição |
|----------------|-----------|
| Campo de texto | permite colar qualquer trecho de publicação |
| Exemplos rápidos | botões para Decreto, Lei e Portaria |
| Resultado visual | exibe classe, nome amigável e confiança |
| Top-3 | mostra probabilidades para as 3 classes |
| Tokens | informa tokens reconhecidos no vocabulário |
| `/health` | endpoint de verificação do servidor |
| `/classificar` | endpoint REST para classificação |

---

## 9. Artefatos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `src/model.py` | arquitetura neural |
| `src/train.py` | treino, avaliação e checkpoint |
| `src/inferencia.py` | pipeline de inferência |
| `src/dataset.py` | Dataset PyTorch |
| `app.py` | interface Flask |
| `models/modelo.pt` | melhor modelo treinado |
| `data/processed/curva_loss.png` | curvas de loss/acurácia |
| `data/processed/matriz_confusao.png` | matriz de confusão |
| `data/processed/historico_treino.json` | histórico numérico do treinamento |

---

## 10. Limitações e Melhorias Futuras

| Limitação | Impacto | Melhoria possível |
|-----------|---------|-------------------|
| Apenas 3 classes | não cobre todo o Diário Oficial | expandir scraper para novas seções |
| Modelo ignora ordem dos tokens | pode confundir textos semelhantes | testar TextCNN, GRU ou LSTM |
| `MAX_LEN=60` | pode truncar textos longos | avaliar percentis reais e ajustar |
| Coleta depende do site | pode sofrer bloqueio WAF | cache local e rotina incremental |

Melhorias futuras:

1. adicionar classes como Licitações, Atos de Pessoal, Concursos e Contas Públicas;
2. coletar e balancear novas categorias;
3. comparar EmbeddingAvg com TextCNN;
4. testar modelos pré-treinados em português, como BERTimbau;
5. criar rotina de avaliação automática na interface.

---

## 11. Conclusão

O projeto alcançou o objetivo principal da disciplina: construir uma solução completa de classificação textual com redes neurais, desde a coleta dos dados até a interface de uso.

A acurácia de **85,83%** demonstra que o modelo aprendeu padrões relevantes para distinguir Leis, Decretos e Portarias. Mesmo utilizando uma arquitetura simples, o resultado é adequado para fins didáticos e mostra a viabilidade do uso de NLP e PyTorch em documentos públicos municipais.

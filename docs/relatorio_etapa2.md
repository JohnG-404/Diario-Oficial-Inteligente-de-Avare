# Relatório da Etapa 2 — Extração, Limpeza e Estruturação

**Projeto:** Diário Oficial Inteligente de Avaré  
**Semana:** 2 de 4

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

Na Etapa 2, a lista de URLs e metadados coletada na Etapa 1 foi transformada em uma base textual estruturada. Foram extraídos textos completos das publicações, aplicadas rotinas de limpeza e criado o arquivo `data/processed/base_textual.csv`.

A base textual final possui aproximadamente **3883 publicações**, das quais **3862 possuem texto válido**. A partir dela, foi gerada uma amostra rotulada balanceada com **600 registros**, distribuídos entre as classes `decreto`, `lei` e `portaria`.

---

## 2. Fontes de Texto

O Diário Oficial de Avaré fornece dois caminhos principais para o conteúdo textual:

| Tipo | URL | Uso no projeto |
|------|-----|----------------|
| Edição completa | `dosp.com.br/exibe_do.php?i=<id>` | edição completa com vários atos |
| Texto individual | `dosp.com.br/leituratexto?p=<id>` | ato individual em HTML |

A extração priorizou as páginas HTML de texto individual quando disponíveis, pois elas contêm o conteúdo de cada ato de forma mais isolada. Para documentos sem texto individual, a extração por PDF permanece como alternativa.

---

## 3. Limpeza e Normalização

As rotinas de limpeza mantiveram o conteúdo fiel ao texto original, removendo apenas ruídos técnicos.

| Transformação | Aplicada | Justificativa |
|---------------|----------|---------------|
| Remoção de espaços múltiplos | sim | padronização |
| Remoção de quebras excessivas | sim | melhora leitura e processamento |
| Remoção de caracteres de controle | sim | evita erros em CSV e NLP |
| Normalização Unicode | sim | padroniza acentos |
| Remoção de acentos | não | preserva português |
| Minúsculas | não nesta etapa | realizado na Etapa 3 |
| Stopwords | não nesta etapa | removidas somente na preparação NLP |

---

## 4. Estrutura da Base Textual

A base foi organizada com os seguintes campos:

| Campo | Descrição |
|-------|-----------|
| `id` | identificador único do registro |
| `data_publicacao` | data no formato `YYYY-MM-DD` |
| `numero_edicao` | número da edição |
| `tipo_ato` | categoria original do site |
| `titulo` | título ou ementa |
| `secretaria` | órgão identificado ou inferido |
| `texto` | conteúdo textual limpo |
| `url_original` | fonte do documento |
| `rotulo` | classe supervisionada para treinamento |

---

## 5. Amostra Rotulada Atual

A versão inicial do projeto utilizava uma amostra pequena e desbalanceada de seis classes. Após a análise exploratória, foi adotada uma amostra mais robusta de três classes principais, diretamente relacionadas ao campo `tipo_ato`.

| Classe | Registros |
|--------|----------:|
| decreto | 200 |
| lei | 200 |
| portaria | 200 |
| **Total** | **600** |

Essa decisão melhora a qualidade do treinamento e evita que o modelo aprenda a partir de classes com pouquíssimos exemplos.

---

## 6. Critério de Rotulagem

A rotulagem foi baseada no campo `tipo_ato`:

| `tipo_ato` original | `rotulo` |
|--------------------|----------|
| Decretos | decreto |
| Leis | lei |
| Portarias | portaria |

A amostra foi balanceada usando 200 registros aleatórios de cada classe, com `random_state=42` para reprodutibilidade.

---

## 7. Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `data/processed/base_textual.csv` | base completa com textos extraídos |
| `data/processed/amostra_rotulada.csv` | 600 registros rotulados |
| `docs/dicionario_campos.md` | descrição formal dos campos |
| `src/extract_text.py` | funções de extração HTML/PDF |
| `src/preprocess.py` | funções de limpeza e normalização |

---

## 8. Conclusão da Etapa 2

A Etapa 2 produziu a base textual necessária para o trabalho de NLP. A revisão da amostra rotulada foi essencial para tornar o projeto mais adequado ao objetivo da disciplina de Redes Neurais: treinar e avaliar um classificador funcional com dados suficientes e classes bem representadas.

# Dicionário de Campos — Base Textual do Diário Oficial de Avaré

**Projeto:** Diário Oficial Inteligente de Avaré  
**Etapa:** 2 — Extração, Limpeza e Estruturação  
**Arquivo descrito:** `data/processed/base_textual.csv`

---

## Visão Geral

A base textual é o produto central da Etapa 2. Cada linha representa **uma publicação individual** extraída do Diário Oficial de Avaré, com seu texto limpo e campos estruturados prontos para uso em modelos de NLP.

---

## Campos da Base

| Campo | Tipo | Formato | Obrigatório | Descrição |
|-------|------|---------|-------------|-----------|
| `id` | string | `DOA-AAAA-NNN` | Sim | Identificador único do registro |
| `data_publicacao` | string | `AAAA-MM-DD` | Sim | Data de publicação no Diário Oficial |
| `numero_edicao` | integer | numérico | Sim | Número sequencial da edição do Diário |
| `tipo_ato` | string | texto livre | Sim | Categoria conforme classificação do site |
| `titulo` | string | texto livre | Sim | Título ou ementa do ato |
| `secretaria` | string | texto livre | Não | Órgão responsável pela publicação |
| `texto` | string | texto livre | Sim | Conteúdo textual limpo e completo |
| `url_original` | string | URL completa | Sim | Link de origem para rastreabilidade |
| `rotulo` | string | ver classes | Não | Classe atribuída manualmente para treino |

---

## Descrição Detalhada dos Campos

### `id`
- **Formato:** `DOA-AAAA-NNN` onde `AAAA` é o ano e `NNN` é sequencial com 3 dígitos
- **Exemplo:** `DOA-2025-001`, `DOA-2026-042`
- **Geração:** atribuído automaticamente pelo pipeline durante a montagem da base
- **Unicidade:** garantida — não há dois registros com o mesmo `id`

---

### `data_publicacao`
- **Formato:** ISO 8601 — `AAAA-MM-DD`
- **Exemplo:** `2025-03-15`, `2026-05-14`
- **Fonte:** coluna `data_publicacao` do CSV gerado na Etapa 1, convertida de `DD/MM/AAAA`
- **Valores ausentes:** não permitido — registros sem data são descartados

---

### `numero_edicao`
- **Tipo:** inteiro positivo
- **Exemplo:** `2732`, `2598`, `2248`
- **Observação:** edições são sequenciais e únicas; uma mesma edição pode conter múltiplos atos (múltiplas linhas na base)
- **Fonte:** coluna `numero_edicao` do CSV da Etapa 1

---

### `tipo_ato`
- **Tipo:** string
- **Valores possíveis (conforme categorias do site):**

| Valor | Descrição |
|-------|-----------|
| `Decretos` | Decretos municipais do Executivo |
| `Portarias` | Portarias de secretários e do prefeito |
| `Atos Legislativos` | Leis ordinárias e complementares |
| `Licitações e Contratos` | Editais, contratos, atas de registro |
| `Concursos Públicos/Processos Seletivos` | Editais e resultados de concursos |
| `Contas Públicas e Instrumentos de Gestão Fiscal` | Balancetes e relatórios LRF |
| `Atos de Pessoal` | Nomeações, exonerações, afastamentos |
| `Atos Administrativos` | Atos internos de gestão |
| `Comunicados` | Avisos e comunicações oficiais |
| `Outros Atos` | Atos que não se enquadram nas demais categorias |

---

### `titulo`
- **Tipo:** string, texto livre
- **Exemplo:** `Decreto 8742 – Crédito Adicional Suplementar`
- **Observação:** pode ser truncado no site; o texto completo está no campo `texto`
- **Comprimento típico:** 30–120 caracteres

---

### `secretaria`
- **Tipo:** string, texto livre
- **Valores comuns:**

| Valor | Observação |
|-------|------------|
| `Secretaria de Administração` | Atos de gestão geral |
| `Secretaria de Saúde` | Saúde pública e vigilância |
| `Secretaria de Educação` | Ensino municipal |
| `Secretaria de Finanças` | Orçamento e finanças |
| `Secretaria de Obras` | Urbanismo e infraestrutura |
| `Secretaria de Meio Ambiente` | Meio ambiente |
| `Secretaria de Transporte` | Transporte público |
| `Não identificada` | Campo não identificável pelo título |

- **Método de extração:** inferência por palavras-chave no título (Etapa 2); será aprimorado com NLP na Etapa 3

---

### `texto`
- **Tipo:** string, texto livre
- **Conteúdo:** texto integral do ato após extração e limpeza
- **Limpeza aplicada** (via `src/preprocess.py`):
  - Remoção de espaços múltiplos e quebras de linha excessivas
  - Remoção de números de página isolados
  - Remoção de caracteres de controle
  - Normalização Unicode NFC
- **O que NÃO foi removido:**
  - Acentos e caracteres especiais do português
  - Letras maiúsculas
  - Stopwords
  - Pontuação
- **Comprimento típico:** 200–2.000 caracteres (atos simples a complexos)
- **Valores ausentes:** permitido quando o PDF é escaneado (OCR não disponível); registrado como string vazia

---

### `url_original`
- **Tipo:** string, URL completa
- **Formatos possíveis:**
  - PDF de edição completa: `https://www.dosp.com.br/exibe_do.php?i=<base64_id>`
  - HTML de ato individual: `https://www.dosp.com.br/leituratexto?p=<base64_id>`
- **Finalidade:** rastreabilidade — permite reprocessar ou auditar a fonte

---

### `rotulo`
- **Tipo:** string
- **Obrigatório:** apenas na `amostra_rotulada.csv`; string vazia na `base_textual.csv` para registros ainda não rotulados
- **Valores possíveis (classes do projeto):**

| Rótulo | Descrição | Termos indicativos |
|--------|-----------|-------------------|
| `decreto` | Decretos e leis municipais | *fica decretado, decreto municipal, lei nº, sanciono* |
| `portaria` | Portarias administrativas | *portaria, resolve, considerando, art. 1º* |
| `ato_pessoal` | Atos de pessoal | *nomear, exonerar, cargo em comissão, servidor, férias, adicional* |
| `licitacao_contrato` | Licitações e contratos | *pregão eletrônico, ata de registro, empresa vencedora, CNPJ, extrato* |
| `edital_concurso` | Editais e concursos | *torna público, processo seletivo, inscrições abertas, concurso, classificação final* |
| `contas_publicas` | Contas e relatórios fiscais | *balancete, receita, despesa, orçamento, LRF, FUNDEB* |

- **Ambiguidades documentadas:** portarias de pessoal podem ser classificadas como `portaria` ou `ato_pessoal` — o critério adotado é: se o ato principal é uma nomeação/exoneração/afastamento, usar `ato_pessoal`; se for regulamentação geral, usar `portaria`

---

## Estatísticas da Amostra Rotulada

| Rótulo | Quantidade | % |
|--------|-----------|---|
| `decreto` | 12 | 28,6% |
| `licitacao_contrato` | 8 | 19,0% |
| `portaria` | 7 | 16,7% |
| `ato_pessoal` | 5 | 11,9% |
| `edital_concurso` | 5 | 11,9% |
| `contas_publicas` | 5 | 11,9% |
| **Total** | **42** | **100%** |

---

## Arquivos Relacionados

| Arquivo | Descrição |
|---------|-----------|
| `data/processed/base_textual.csv` | Base completa com todos os campos |
| `data/processed/amostra_rotulada.csv` | Subconjunto com campo `rotulo` preenchido |
| `data/processed/diario_avare.db` | Base em SQLite para consultas relacionais |
| `data/diario_avare.csv` | CSV da Etapa 1 (metadados e URLs) |
| `src/extract_text.py` | Script de extração de texto |
| `src/preprocess.py` | Script de limpeza e normalização |

---

*Última atualização: Etapa 2 — Semana 2*

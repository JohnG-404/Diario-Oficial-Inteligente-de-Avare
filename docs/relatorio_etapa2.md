# Relatório da Etapa 2 — Extração, Limpeza e Estruturação

**Projeto:** Diário Oficial Inteligente de Avaré  
**Semana:** 2 de 4

---

## Grupo
- Gabriel Bianco Sanches - 9º termo 
- Gabriel Santana dos Santos - 9º termo
- Guilherme Monteiro da Luz - 9º termo 
- Joao Gabriel Pereira Cardozo - 9º termo 
- Joao Gabriel Godoy Pereira - 9º termo 
- Lucas Nakamura Rodrigues - 9º termo 
- Lucas Vaz Barbosa - 9º termo 
- Pedro Lucas Campos - 7º termo 

## Repositorio

- **Github:** https://github.com/JohnG-404/Diario-Oficial-Inteligente-de-Avare

---

## 1. Resumo Executivo

Nesta etapa transformamos a lista de URLs e metadados coletada na Etapa 1 em uma **base textual limpa e estruturada**, pronta para ser usada por modelos de NLP. Foram gerados 42 registros com texto extraído, campos padronizados e rótulos atribuídos manualmente para 6 classes distintas.

---

## 2. Atividade 1 — Extração de Texto

### Fontes de texto do Diário Oficial de Avaré

O site oferece dois tipos de URL para acesso ao conteúdo:

| Tipo | URL | Resultado |
|------|-----|-----------|
| Edição completa | `dosp.com.br/exibe_do.php?i=<id>` | PDF com múltiplos atos |
| Texto individual | `dosp.com.br/leituratexto?p=<id>` | HTML com um ato específico |

**Decisão adotada:** utilizamos prioritariamente as URLs de texto individual (`leituratexto`) por retornarem HTML limpo com o conteúdo de um único ato, simplificando a extração. Para registros sem `url_texto`, baixamos o PDF completo e extraímos com `pdfplumber`.

### Resultado da extração

- **42 registros processados**
- Extração via HTML: 38 registros (90%)
- Extração via PDF: 4 registros (10%)
- PDFs escaneados encontrados: 0 (todos eram PDFs digitais)
- Registros com texto vazio: 0

### Observação sobre PDFs

Os PDFs do Diário Oficial de Avaré são **PDFs digitais** (não escaneados), o que permitiu extração direta com `pdfplumber` sem necessidade de OCR. Caso PDFs escaneados sejam encontrados em edições mais antigas, seria necessário usar `pytesseract`.

---

## 3. Atividade 2 — Limpeza e Normalização

### Transformações aplicadas (via `src/preprocess.py`)

| Transformação | Exemplo antes | Exemplo depois |
|---------------|---------------|----------------|
| Espaços múltiplos | `"Decreto  123  "` | `"Decreto 123"` |
| Quebras de linha excessivas | `"Art. 1º\n\n\n\nArt. 2º"` | `"Art. 1º\n\nArt. 2º"` |
| Números de página isolados | `"\n 47 \n"` | `""` |
| Caracteres de controle | `"\x0c"` (form feed) | removido |
| Normalização Unicode | `"Avaré"` (NFD) | `"Avaré"` (NFC) |
| Traço duplo | `"Art. 1º -- resolve"` | `"Art. 1º - resolve"` |

### O que NÃO foi modificado (conforme orientação do guia)

- Acentos e caracteres especiais do português — importantes semanticamente
- Letras maiúsculas — serão normalizadas na Etapa 3
- Stopwords — o modelo pode precisar delas para contexto
- Pontuação — mantida para preservar estrutura dos atos

---

## 4. Atividade 3 — Estruturação da Base

### Campos criados

A base foi organizada com os 9 campos especificados no guia. Ver `docs/dicionario_campos.md` para descrição completa de cada campo.

### Exemplo de registro

```
id:               DOA-2026-001
data_publicacao:  2026-05-14
numero_edicao:    2732
tipo_ato:         Decretos
titulo:           Decreto 8742 – Crédito Adicional Suplementar
secretaria:       Secretaria de Finanças
texto:            DECRETO Nº 8.742, DE 14 DE MAIO DE 2026.
                  Abre Crédito Adicional Suplementar no valor de R$ 224.000,00...
url_original:     https://www.dosp.com.br/exibe_do.php?i=ODE3ODM2
rotulo:           decreto
```

### Arquivos gerados

| Arquivo | Registros | Descrição |
|---------|-----------|-----------|
| `data/processed/base_textual.csv` | 42 | Base completa com texto limpo |
| `data/processed/amostra_rotulada.csv` | 42 | Todos os registros rotulados |
| `data/processed/diario_avare.db` | 42 | Versão SQLite |

---

## 5. Atividade 4 — Definição de Classes e Rotulagem

### Classes definidas

Foram definidas 6 classes baseadas nos tipos de atos mais frequentes no Diário Oficial de Avaré:

| Classe | Critério de classificação |
|--------|--------------------------|
| `decreto` | Atos do executivo com força normativa: decretos municipais, leis sancionadas |
| `portaria` | Atos internos de gestão e regulamentação administrativa geral |
| `ato_pessoal` | Nomeações, exonerações, afastamentos, concessão de férias/adicionais |
| `licitacao_contrato` | Editais de pregão, extratos de contrato, atas de registro de preços |
| `edital_concurso` | Abertura, convocação e homologação de concursos e processos seletivos |
| `contas_publicas` | Balancetes, relatórios LRF, prestações de contas, demonstrativos fiscais |

### Distribuição dos rótulos

| Classe | Registros | % |
|--------|-----------|---|
| decreto | 12 | 28,6% |
| licitacao_contrato | 8 | 19,0% |
| portaria | 7 | 16,7% |
| ato_pessoal | 5 | 11,9% |
| edital_concurso | 5 | 11,9% |
| contas_publicas | 5 | 11,9% |

### Ambiguidades de rotulagem encontradas

1. **Portarias de pessoal vs. ato_pessoal:** muitas portarias tratam de nomeações e exonerações. O critério adotado: se o ato **principal** do texto é a movimentação de pessoas (nomear, exonerar, conceder férias), classificar como `ato_pessoal`; se for uma regulamentação de processo, classificar como `portaria`.

2. **Leis vs. decretos:** leis municipais sancionadas pelo prefeito foram classificadas como `decreto` por terem força normativa similar. Caso o volume de leis aumente, criar classe separada `lei` na Etapa 3.

3. **Avisos de licitação vs. extratos de contrato:** ambos classificados como `licitacao_contrato` por referirem ao mesmo domínio funcional.

---

## 6. Atividade 5 — Pipeline e Organização

### Fluxo de dados da Etapa 2

```
data/diario_avare.csv          (Etapa 1 — scraper.py)
         ↓
src/extract_text.py            → baixa PDF / extrai HTML
         ↓
src/preprocess.py              → limpa e normaliza texto
         ↓
data/processed/base_textual.csv
         ↓
[rotulagem manual]
         ↓
data/processed/amostra_rotulada.csv  → insumo direto para Etapa 3
```

### Responsabilidades dos scripts

| Script | Função | Funções principais |
|--------|--------|--------------------|
| `src/extract_text.py` | Extração de PDF e HTML | `baixar_pdf()`, `extrair_de_pdf()`, `extrair_de_html()` |
| `src/preprocess.py` | Limpeza e normalização | `limpar_texto()`, `normalizar_texto()`, `processar()` |

---

## 7. Próximos Passos (Etapa 3)

- Tokenizar os textos da `amostra_rotulada.csv`
- Construir vocabulário com base nos textos processados
- Remover stopwords e aplicar normalização adicional (minúsculas)
- Codificar os rótulos como inteiros para uso no PyTorch
- Dividir a base em treino (70%), validação (15%) e teste (15%)
- Implementar a classe `DiarioDataset` compatível com `torch.utils.data.Dataset`

---

*Relatório da Etapa 2 — Semana 2*

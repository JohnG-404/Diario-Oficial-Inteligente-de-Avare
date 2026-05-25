# Diário Oficial Inteligente de Avaré

**Projeto de NLP — Coleta, Processamento e Classificação de Publicações Oficiais**

> Transformando o Diário Oficial do Município de Avaré/SP em uma base de dados organizada e inteligente.

---

## Grupo

| Nome |
|------|
| Gabriel Bianco Sanches |
| Gabriel Santana dos Santos |  
| Guilherme Monteiro da Luz |  
| Joao Gabriel Pereira Cardozo |  
| Joao Gabriel Godoy Pereira |  
| Lucas Nakamura Rodrigues |  
| Lucas Vaz Barbosa |  
| Pedro Lucas Campos |  

---

## Visão Geral do Projeto

O Diário Oficial de Avaré é publicado pela plataforma **DiOE** (P&P Colibri) em `imprensaoficialmunicipal.com.br/avare`. Este projeto aplica técnicas de **web scraping**, **processamento de linguagem natural (NLP)** e **deep learning** para:

1. Coletar automaticamente as publicações do Diário Oficial
2. Extrair e limpar o texto de cada ato
3. Tokenizar e preparar os dados para treinamento
4. Treinar um classificador textual por tipo de ato

---

## Etapas do Projeto

| Etapa | Semana | Objetivo | Status |
|-------|--------|----------|--------|
| **Etapa 1** | Semana 1 | Exploração do site e coleta automatizada | Concluída |
| **Etapa 2** | Semana 2 | Extração de texto, limpeza e organização | Em andamento |
| **Etapa 3** | Semana 3 | NLP, tokenização e Dataset PyTorch | Pendente |
| **Etapa 4** | Semana 4 | Treinamento, avaliação e apresentação | Pendente |

---

## Estrutura do Repositório

```
diario-avare-nlp/
│
├── data/
│   ├── raw/                        # PDFs e HTMLs brutos baixados
│   ├── processed/                  # Dados após limpeza e pré-processamento
│   └── diario_avare.csv            # Lista de publicações (saída do scraper)
│
├── notebooks/
│
├── src/
│   ├── scraper.py      # Etapa 1 — Coleta automatizada
│
├── requirements.txt
├── README.md
└── relatorio_final.md
```

---

## Como Rodar

### Pré-requisitos

- Python 3.10+
- Git
- Acesso à internet via **rede local** (não funciona em servidores de nuvem — veja nota abaixo)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/diario-avare-nlp.git
cd diario-avare-nlp
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute cada etapa em ordem

```bash
# Etapa 1 — Coleta
python src/scraper.py

# Etapa 2 — Extração de texto
python src/extract_text.py

# Etapa 3 — Pré-processamento
python src/preprocess.py

# Etapa 4 — Treinamento
python src/train.py
```

---

## Nota Importante: Bloqueio WAF

O servidor `imprensaoficialmunicipal.com.br` implementa um **Web Application Firewall (WAF)** que bloqueia requisições originadas de IPs de datacenters (AWS, Google Cloud, Azure etc.), retornando `403 Host not in allowlist`.

**Solução:** execute todos os scripts a partir de sua **rede doméstica ou institucional** (não em máquinas virtuais de nuvem). O scraper inclui lógica de retry com backoff exponencial para lidar com falhas transitórias.

---

## Estrutura do CSV Principal

Arquivo: `data/diario_avare.csv`

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `data_publicacao` | string (ISO 8601) | Data da edição | `2026-05-14` |
| `numero_edicao` | string | Número da edição | `2732` |
| `titulo_ato` | string | Título do ato publicado | `Decreto 8742` |
| `tipo_ato` | string | Categoria (rótulo de classificação) | `Decretos` |
| `url_documento` | string | Link para a edição completa (PDF) | `https://dosp.com.br/...` |
| `url_texto` | string | Link para o texto individual do ato | `https://dosp.com.br/...` |
| `secretaria` | string | Órgão responsável (inferido) | `Secretaria de Educação` |

---

## Mapeamento do Site (Etapa 1)

| URL | Conteúdo | Tecnologia |
|-----|----------|------------|
| `/avare` | Página principal com filtros e lista de edições | HTML + JS dinâmico |
| `/pesquisar.php?c=avare` | Busca por texto | HTML estático |
| `/listaatos.php?c=Avaré&s=Decretos` | Lista de decretos | HTML estático ✅ |
| `/listaatos.php?c=Avaré&s=Portarias` | Lista de portarias | HTML estático ✅ |
| `/listaatos.php?c=Avaré&s=Leis` | Lista de leis | HTML estático ✅ |
| `dosp.com.br/exibe_do.php?i=<id>` | Edição completa (PDF) | PDF |
| `dosp.com.br/leituratexto?p=<id>` | Texto individual do ato | HTML estático ✅ |

**Padrão dos IDs:** os parâmetros `i` e `p` são strings codificadas em Base64. Ex.: `ODE3ODM2` → `817836`.

---

## Seções do Diário Oficial de Avaré

| Seção | Nº de Atos |
|-------|------------|
| Atos Oficiais | 4.001 |
| Outros Atos | 3.974 |
| Contas Públicas e Instrumentos de Gestão Fiscal | 2.213 |
| Licitações e Contratos | 700 |
| Concursos Públicos / Processos Seletivos | 595 |
| Atos Legislativos | 535 |
| Atos de Pessoal | 260 |
| Errata | 116 |
| Conselhos Municipais | 90 |
| Editais | 38 |
| Ineditoriais | 67 |
| Comunicados | 20 |
| Advertências / Notificações | 188 |
| Atos Administrativos | 80 |

---

## Modelos Implementados (Etapa 4)

| Modelo | Descrição | Parâmetros (aprox.) |
|--------|-----------|---------------------|
| **TextCNN** | Convolução 1D com múltiplos kernel sizes (2, 3, 4) | ~350k |
| **BiLSTM** | LSTM bidirecional de 2 camadas | ~800k |

Referência: Kim (2014) — *Convolutional Neural Networks for Sentence Classification*

---

## Referências

- **Site do Diário Oficial de Avaré:** https://imprensaoficialmunicipal.com.br/avare
- **Projeto de referência (TCU):** https://github.com/netoferraz/acordaos-tcu
- **Documentação BeautifulSoup:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **PyTorch:** https://pytorch.org/docs/stable/
- **Pandas:** https://pandas.pydata.org/docs/
- **Beautiful Soup:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Kim (2014) — TextCNN:** https://arxiv.org/abs/1408.5882

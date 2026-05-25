# Relatório de Exploração — Etapa 1
## Diário Oficial Inteligente de Avaré

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

## 1. Identificação

- **Disciplina:** Processamento de Linguagem Natural / Engenharia de Dados
- **Semana:** 1 de 4
- **Entregável:** Exploração do site, configuração do ambiente e coleta preliminar
- **Site analisado:** https://imprensaoficialmunicipal.com.br/avare

---

## 2. Atividade 1 — Exploração Manual do Site

### 2.1 Contexto da Plataforma

O Diário Oficial de Avaré é hospedado na plataforma **DiOE** (Diário Oficial Eletrônico), desenvolvida pela empresa **P&P Colibri**, sob o domínio `imprensaoficialmunicipal.com.br`. A mesma plataforma atende outros municípios do estado de São Paulo. O sistema de publicação e visualização de atos está distribuído entre dois domínios:

| Domínio | Função |
|---------|--------|
| `imprensaoficialmunicipal.com.br` | Interface pública de navegação e listagem |
| `dosp.com.br` | Armazenamento e visualização dos documentos (PDF e HTML) |

---

### 2.2 Estrutura de Navegação

A página principal (`/avare`) apresenta:

- **Menu superior:** Início | Pesquisar | Listar Atos (Leis, Decretos, Portarias) | Push
- **Filtro por data:** campos de data inicial e data final (interface de formulário)
- **Filtro por seção:** lista lateral com 17 categorias e contagem de atos
- **Área central:** "Edições Veiculadas" — carregada dinamicamente via JavaScript
- **Rodapé lateral:** contador de recursos economizados (água, energia, papel)

---

### 2.3 Tipos de Documentos Disponíveis

Todos os documentos do Diário Oficial de Avaré são **publicados como PDF** e acessados via `dosp.com.br/exibe_do.php`. Adicionalmente, atos individuais podem ter seu texto exibido em HTML via `dosp.com.br/leituratexto`.

| Formato | URL | Observação |
|---------|-----|------------|
| **PDF completo** | `dosp.com.br/exibe_do.php?i=<id>` | Edição inteira, com múltiplos atos |
| **HTML individual** | `dosp.com.br/leituratexto?p=<id>` | Texto de um ato específico — nem todos possuem |

Exemplo de PDF acessado (Edição 2732, 14/05/2026):
- Portaria nº 1.113/2026 — Enquadramento de Profissionais da Educação
- Decreto 8742/2026 — Crédito Adicional Suplementar (R$ 224.000,00)
- Edital de Classificação Final — Concurso Público 03/2025

---

### 2.4 Padrões de URL Identificados

```
# Página principal
https://imprensaoficialmunicipal.com.br/avare

# Pesquisa por texto
https://imprensaoficialmunicipal.com.br/pesquisar.php?c=avare

# Listagem de atos por categoria (URL ESTÁTICA — funciona com requests)
https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Leis
https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Decretos
https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Portarias

# Edição completa (PDF) — parâmetro 'i' = ID numérico em Base64
https://www.dosp.com.br/exibe_do.php?i=ODE3ODM2
# ODE3ODM2 → Base64 decode → 817836

# Texto individual de ato — parâmetro 'p' = ID numérico em Base64
https://www.dosp.com.br/leituratexto?p=MjYyMjIxMw==
# MjYyMjIxMw== → Base64 decode → 2622213
```

**Descoberta importante:** os IDs são números inteiros serializados em Base64. Isso significa que é possível iterar por edições simplesmente codificando IDs consecutivos — uma abordagem alternativa de coleta que não depende de navegar pelo HTML.

---

### 2.5 Campos de Metadados Visíveis

A tabela nas páginas `/listaatos.php` expõe os seguintes campos por ato:

| Campo na Tabela | Campo no CSV | Observação |
|-----------------|-------------|------------|
| Título | `titulo_ato` | Truncado com "(...)" — texto completo no documento |
| Data | `data_publicacao` | Formato DD/MM/AAAA → convertido para ISO 8601 |
| Edição | `numero_edicao` | Número sequencial da edição (ex.: 2732) |
| Ano | — | Ano da administração municipal (não incluído no CSV) |
| Link "Abrir Edição" | `url_documento` | PDF completo da edição |
| Link "Visualizar" | `url_texto` | HTML do ato individual (nem sempre disponível) |

O campo `secretaria` não está disponível na listagem — é **inferido** a partir do título do ato por meio de heurística de palavras-chave (será aprimorado com NLP na Etapa 3).

---

### 2.6 Seções do Diário Oficial

A página principal lista 17 seções temáticas com contagem total de atos:

| Seção | Total |
|-------|-------|
| Atos Oficiais | 4.001 |
| Outros Atos | 3.974 |
| Contas Públicas e Instrumentos de Gestão Fiscal | 2.213 |
| Licitações e Contratos | 700 |
| Concursos Públicos / Processos Seletivos | 595 |
| Atos Legislativos | 535 |
| Atos de Pessoal | 260 |
| Errata | 116 |
| Ineditoriais | 67 |
| Conselhos Municipais | 90 |
| Editais | 38 |
| Comunicados | 20 |
| Advertências / Notificações | 188 |
| Atos Administrativos | 80 |
| Atos Normativos | 1 |
| Publicidade Oficial | 1 |
| Vigilância Sanitária | 2 |
| **TOTAL** | **~12.966** |

---

### 2.7 Dificuldades Encontradas

| Dificuldade | Impacto | Solução Adotada |
|-------------|---------|-----------------|
| **Bloqueio WAF (403)** | Alto — impede requests de servidores cloud | Executar da rede local; usar headers realistas |
| **JS dinâmico na home** | Médio — edições da página principal não carregam | Usar `/listaatos.php` (estático) em vez da home |
| **Títulos truncados** | Baixo — metadados incompletos | Buscar texto completo via `url_texto` |
| **Sem campo secretaria** | Médio — dado importante para análise | Inferência por palavras-chave (Etapa 3: NLP) |
| **PDFs sem seleção de texto** | Médio — extração pode ser difícil | Verificar se PDF é digital ou escaneado; usar pdfplumber |

---

## 3. Atividade 2 — Configuração do Ambiente

### 3.1 Dependências instaladas

```bash
pip install requests beautifulsoup4 pandas          # Etapa 1
pip install playwright && playwright install chromium # (opcional, para JS dinâmico)
pip install torch torchvision                        # Etapas 3 e 4
pip install matplotlib scikit-learn                  # Etapa 4
```

Arquivo `requirements.txt` gerado com `pip freeze`.

### 3.2 Estrutura de pastas

Criada conforme especificado no enunciado. Ver `README.md` para detalhes.

### 3.3 Repositório Git

- Repositório criado no GitHub com branches por integrante
- Commits frequentes com mensagens descritivas (convenção: `feat:`, `fix:`, `docs:`)
- `.gitignore` configurado para excluir `venv/`, `data/raw/*.pdf`, `__pycache__/`

---

## 4. Atividade 3 — Comparação com o Projeto TCU

### 4.1 Análise do projeto `netoferraz/acordaos-tcu`

O projeto TCU coletou **acórdãos do Tribunal de Contas da União** de 1992 a 2019, totalizando 73.371 documentos. Sua arquitetura usa:

- **Selenium** para navegar no site do TCU (JavaScript dinâmico intenso)
- **Scrapy** para coleta em larga escala de múltiplas páginas
- **Dataset publicado no Kaggle** com metadados estruturados

### 4.2 Semelhanças com nosso projeto

| Aspecto | Projeto TCU | Nosso Projeto (Avaré) |
|---------|------------|----------------------|
| Tipo de dado | Documentos jurídico-administrativos | Documentos jurídico-administrativos |
| Objetivo | Coleta → estruturação → dataset | Coleta → estruturação → classificação |
| Pipeline | scraping → extração → processamento | scraping → extração → processamento |
| Formato | PDF + HTML | PDF + HTML |
| Metadados | Data, número, relator, tipo | Data, edição, título, seção |

### 4.3 Diferenças

| Aspecto | Projeto TCU | Nosso Projeto (Avaré) |
|---------|------------|----------------------|
| Escala | 73.371 documentos / 27 anos | ~12.966 atos / escopo 2025-2026 |
| Complexidade técnica | Alta (Selenium + Scrapy) | Moderada (requests + BS4 suficiente) |
| JS dinâmico | Intenso — Selenium necessário | Parcial — apenas a home page |
| Âmbito | Federal / controle externo | Municipal / gestão administrativa |
| Tarefa ML | Não aplicada | Classificação por tipo de ato |

### 4.4 O que reutilizamos do TCU

- **Lógica do pipeline em etapas:** separar coleta, extração, processamento e modelagem em scripts independentes
- **Padrão de nomeação de scripts:** `scraper.py`, `extract_text.py`, `preprocess.py`
- **Abordagem de metadados mínimos** no CSV (data, número, título, tipo, URL)
- **Documentação do processo** (README detalhado + relatório de exploração)

### 4.5 Decisões de design que consideramos interessantes

1. **Separação entre coleta e extração de texto**: o TCU separou o download dos documentos da extração do conteúdo — seguimos o mesmo princípio para facilitar reprocessamento sem nova coleta
2. **Dataset publicado como artefato reutilizável**: inspirador para nossa Etapa 4 (gerar CSV final que possa ser usado por outros projetos)
3. **Uso de múltiplas ferramentas complementares**: Selenium para navegação + Scrapy para coleta — mostra que não existe "uma ferramenta certa", mas sim a mais adequada para cada etapa

---

## 5. Atividade 4 — Teste com requests e BeautifulSoup

### 5.1 Requisição básica

```python
import requests
from bs4 import BeautifulSoup

URL = 'https://imprensaoficialmunicipal.com.br/avare'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'}

response = requests.get(URL, headers=headers, timeout=15)
# Resultado: 403 Forbidden — "Host not in allowlist"
# Causa: WAF bloqueia IPs de datacenter
```

**Solução:** executar da rede local. O bloqueio é baseado em IP, não em User-Agent.

### 5.2 Resultado da coleta via /listaatos.php

```python
URL = 'https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Portarias'
# Resultado quando executado da rede local: 200 OK
# HTML completo com tabela de atos — sem necessidade de JavaScript
```

Totais coletados na Atividade 6:
- Portarias: 19 registros (2018–2026)
- Decretos: 10 registros (2025–2026)
- Leis: 5 registros (2025–2026)
- **Total: 34 publicações** salvas em `data/diario_avare.csv`

---

## 6. Atividade 5 — Decisão Técnica: requests vs. Playwright

### 6.1 Diagnóstico

| Teste | Resultado |
|-------|-----------|
| `requests` na home page (`/avare`) | ✅ Retorna HTML mas sem tabela de edições (JS necessário) |
| `requests` em `/listaatos.php` | ✅ Retorna HTML completo com tabela de atos |
| `requests` em `/pesquisar.php` | ✅ Retorna HTML do formulário de busca |
| `requests` em `dosp.com.br/leituratexto` | ✅ Retorna HTML com texto do ato |
| `requests` em `dosp.com.br/exibe_do.php` | ✅ Retorna PDF completo |

### 6.2 Decisão

```
DECISÃO TÉCNICA: requests + BeautifulSoup para as páginas de listagem
(/listaatos.php) e textos individuais (leituratexto).

Playwright seria necessário APENAS para capturar a lista de edições
da página principal (/avare), que é renderizada via JavaScript.

Para os objetivos da Etapa 1, as páginas /listaatos.php são suficientes
e cobrem todas as categorias de atos disponíveis.
```

### 6.3 Comparativo de ferramentas

| Ferramenta | Prós | Contras | Nossa Decisão |
|------------|------|---------|---------------|
| **requests + BS4** | Simples, rápido, sem overhead | Não executa JavaScript | **✅ Usar para /listaatos.php** |
| **Playwright** | Executa JS, simula navegador real | Mais pesado, mais complexo | Usar se precisar da home page |
| **Selenium** | Bem documentado, amplo suporte | Lento, depende de driver | Não necessário no estágio atual |
| **Scrapy** | Pipeline assíncrono, muito rápido | Curva de aprendizado alta | Reservar para escala maior |

---

## 7. Atividade 6 — Lista Preliminar de Publicações

### 7.1 CSV gerado

**Arquivo:** `data/diario_avare.csv`  
**Registros:** 34 publicações  
**Período:** Janeiro/2025 a Maio/2026  

### 7.2 Amostra dos dados coletados

```
data_publicacao | numero_edicao | titulo_ato                              | tipo_ato  | secretaria
2026-05-14      | 2732          | Decreto 8742 – Crédito Adicional...     | Decretos  | Secretaria de Finanças
2026-05-14      | 2732          | Portaria 1113 – Enquadramento PEB       | Portarias | Secretaria de Educação
2025-07-31      | 2493          | Lei 4.205 – Organização Municipal       | Leis      | Secretaria de Administração
2025-05-29      | 2424          | Lei 4.180 – Saúde Pública               | Leis      | Secretaria de Saúde
```

### 7.3 Código de coleta

Ver `src/scraper.py` — função `coletar_lista_atos()`.

---

## 8. Conclusões da Etapa 1

### O que funcionou bem
- As páginas `/listaatos.php` respondem com HTML estático completo
- A estrutura da tabela é consistente entre diferentes tipos de atos
- Os textos individuais (`leituratexto`) são ricos e bem formatados para extração NLP
- Os IDs em Base64 permitem acesso direto a qualquer ato ou edição

### Desafios a superar nas próximas etapas
- Extração de texto dos PDFs (verificar se são digitais ou escaneados)
- Identificação da secretaria responsável (campo não estruturado)
- Coleta das seções com maior volume ("Atos Oficiais" e "Outros Atos" com >3.000 atos cada)
- Volume de dados: ampliar para todas as 17 seções (atualmente apenas 3)

### Próximos passos (Etapa 2)
1. Iterar por todas as seções disponíveis e expandir o CSV
2. Para cada `url_texto` disponível, extrair o texto completo via `extract_text.py`
3. Aplicar limpeza mais robusta (remover cabeçalhos/rodapés do PDF, normalizar encoding)
4. Enriquecer o campo `secretaria` com extração baseada em expressões regulares
5. Salvar os textos em `data/processed/diario_avare_textos.csv`


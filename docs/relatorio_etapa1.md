# Relatório de Exploração — Etapa 1
## Diário Oficial Inteligente de Avaré

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

## 1. Identificação

- **Disciplina:** Redes Neurais e IA Aplicada
- **Semana:** 1 de 4
- **Entregável:** exploração do site, configuração do ambiente e coleta preliminar
- **Site analisado:** https://imprensaoficialmunicipal.com.br/avare

---

## 2. Objetivo da Etapa

A Etapa 1 teve como objetivo compreender a estrutura do Diário Oficial de Avaré, mapear as formas de navegação disponíveis e construir a primeira rotina de coleta automatizada. O resultado esperado era uma base inicial contendo metadados como data, edição, tipo de ato, título e URLs de origem.

---

## 3. Exploração Manual do Site

O Diário Oficial de Avaré é disponibilizado pela plataforma DiOE, com navegação pública pelo domínio `imprensaoficialmunicipal.com.br` e visualização dos documentos pelo domínio `dosp.com.br`.

| Domínio | Função |
|---------|--------|
| `imprensaoficialmunicipal.com.br` | Listagem, busca e navegação por seções |
| `dosp.com.br` | Visualização dos textos e edições completas |

A página principal apresenta filtros por data, seções laterais, campo de busca e área de edições. Parte da página principal depende de JavaScript, mas as páginas de listagem por tipo de ato funcionam com HTML estático.

---

## 4. Padrões de URL Identificados

```text
https://imprensaoficialmunicipal.com.br/avare
https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Leis
https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Decretos
https://imprensaoficialmunicipal.com.br/listaatos.php?c=Avaré&s=Portarias
https://www.dosp.com.br/exibe_do.php?i=<id>
https://www.dosp.com.br/leituratexto?p=<id>
```

A coleta final do projeto concentrou-se em três categorias com grande volume e boa consistência textual: **Leis, Decretos e Portarias**.

---

## 5. Campos Coletados

| Campo | Descrição |
|-------|-----------|
| `data_publicacao` | data da publicação no formato ISO |
| `numero_edicao` | número da edição |
| `titulo_ato` | título ou ementa resumida |
| `tipo_ato` | categoria do site |
| `url_documento` | URL da edição completa |
| `url_texto` | URL do texto individual, quando disponível |
| `secretaria` | órgão inferido por heurística |

---

## 6. Seções Relevantes

A exploração identificou várias seções disponíveis no portal, incluindo Atos Oficiais, Atos Legislativos, Licitações e Contratos, Concursos, Contas Públicas e Atos de Pessoal. Para a versão final do classificador, foram priorizadas as seções com melhor representatividade no corpus coletado.

Distribuição observada na base textual:

| Tipo de ato | Quantidade |
|-------------|-----------:|
| Decretos | 2291 |
| Leis | 1351 |
| Portarias | 241 |

---

## 7. Decisão Técnica: requests + BeautifulSoup

A coleta foi implementada com `requests` e `BeautifulSoup`, pois as páginas `/listaatos.php` retornam HTML estático com os dados necessários. O uso de Playwright/Selenium foi considerado desnecessário para o escopo atual, já que a navegação pela home é a principal parte dependente de JavaScript.

| Ferramenta | Decisão |
|------------|---------|
| requests + BeautifulSoup | usada na coleta principal |
| Playwright | opcional para páginas dinâmicas |
| Selenium | não necessário |
| Scrapy | reservado para expansão futura |

---

## 8. Dificuldades Encontradas

| Dificuldade | Impacto | Solução |
|-------------|---------|---------|
| Bloqueio WAF | Pode impedir coleta em redes de datacenter | executar em rede local |
| JavaScript na home | Impede leitura direta das edições pela home | usar `/listaatos.php` |
| Campo secretaria ausente | Não há metadado direto | inferência por palavras-chave |
| Grande volume de atos | Coleta completa pode ser demorada | priorização de categorias principais |

---

## 9. Conclusão da Etapa 1

A Etapa 1 confirmou que o site pode ser coletado de forma programática usando páginas estáticas de listagem. A estrutura encontrada foi suficiente para construir a base inicial e viabilizar as etapas seguintes de extração, limpeza, NLP e treinamento neural.

A decisão de trabalhar inicialmente com Leis, Decretos e Portarias foi consolidada posteriormente na EDA, por serem as classes com maior volume e melhor equilíbrio para treinamento supervisionado.

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime
from pathlib import Path

# ─── Configuração de logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Constantes ───────────────────────────────────────────────────────────────
BASE_URL = "https://imprensaoficialmunicipal.com.br"
MUNICIPIO = "avare"
MUNICIPIO_PARAM = "Avaré"   # usado nos parâmetros de URL (com acento)

# Todas as seções disponíveis no Diário Oficial de Avaré
# (descobertas na exploração manual da página principal)
SECOES = {
    "Leis": "Atos Legislativos",
    "Decretos": "Atos Oficiais",
    "Portarias": "Atos Oficiais",
}

# Mapeamento completo de seções (para referência / uso futuro)
TODAS_SECOES = [
    "Advertências / Notificações",    # 188 atos
    "Atos Administrativos",           # 80 atos
    "Atos de Pessoal",                # 260 atos
    "Atos Legislativos",              # 535 atos
    "Atos Normativos",                # 1 ato
    "Atos Oficiais",                  # 4001 atos
    "Comunicados",                    # 20 atos
    "Concursos Públicos/Processos Seletivos",  # 595 atos
    "Conselhos Municipais",           # 90 atos
    "Contas Públicas e Instrumentos de Gestão Fiscal",  # 2213 atos
    "Editais",                        # 38 atos
    "Errata",                         # 116 atos
    "Ineditoriais",                   # 67 atos
    "Licitações e Contratos",         # 700 atos
    "Outros Atos",                    # 3974 atos
    "Publicidade Oficial",            # 1 ato
    "Vigilância Sanitária",           # 2 atos
]

# Headers simulando um navegador real — necessário para evitar bloqueio WAF
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
    "Connection": "keep-alive",
    "Referer": f"{BASE_URL}/{MUNICIPIO}",
}

OUTPUT_DIR = Path(__file__).parent.parent / "data"


# ─── Funções de coleta ─────────────────────────────────────────────────────────

def fazer_requisicao(url: str, tentativas: int = 3) -> requests.Response | None:
    """
    Realiza requisição HTTP com retry automático e backoff exponencial.
    Retorna None se todas as tentativas falharem.
    """
    for i in range(tentativas):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp
            elif resp.status_code == 403:
                log.error(
                    f"403 Forbidden em {url}. "
                    "O servidor bloqueia IPs de datacenters. "
                    "Execute este script da sua rede local."
                )
                return None
            else:
                log.warning(f"Status {resp.status_code} em {url} (tentativa {i+1}/{tentativas})")
        except requests.exceptions.Timeout:
            log.warning(f"Timeout em {url} (tentativa {i+1}/{tentativas})")
        except requests.exceptions.ConnectionError as e:
            log.warning(f"Erro de conexão em {url}: {e} (tentativa {i+1}/{tentativas})")

        if i < tentativas - 1:
            espera = 2 ** i          # backoff: 1s, 2s, 4s
            log.info(f"Aguardando {espera}s antes de tentar novamente...")
            time.sleep(espera)

    log.error(f"Falha após {tentativas} tentativas: {url}")
    return None


def explorar_pagina_principal() -> dict:
    """
    Atividade 1 — Exploração da página principal.
    Retorna um dicionário com informações sobre a estrutura do site.
    """
    url = f"{BASE_URL}/{MUNICIPIO}"
    log.info(f"Explorando página principal: {url}")

    resp = fazer_requisicao(url)
    if not resp:
        return {"erro": "Não foi possível acessar a página principal"}

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extrai título
    titulo = soup.title.string if soup.title else "Sem título"

    # Conta links
    links = soup.find_all("a", href=True)

    # Extrai itens do menu de navegação
    menu_links = []
    for link in links:
        href = link["href"]
        texto = link.get_text(strip=True)
        if href.startswith(BASE_URL) or href.startswith("/"):
            menu_links.append({"url": href, "texto": texto})

    # Extrai contagem por seção (listadas na barra lateral)
    secoes_info = []
    for item in soup.find_all("li"):
        txt = item.get_text(strip=True)
        if txt and "(" in txt and ")" in txt:
            # Formato: "(188) Advertências / Notificações"
            try:
                contagem = int(txt.split("(")[1].split(")")[0])
                nome_secao = txt.split(") ")[1] if ") " in txt else txt
                secoes_info.append({"secao": nome_secao, "total_atos": contagem})
            except (ValueError, IndexError):
                pass

    resultado = {
        "titulo": titulo,
        "url": url,
        "total_links": len(links),
        "menu_navegacao": menu_links[:10],
        "secoes_encontradas": secoes_info,
        "observacoes": [
            "Site usa HTML server-side rendering",
            "Página principal tem seção de edições carregada dinamicamente (JavaScript)",
            "Páginas /listaatos.php são HTML estático — acessíveis via requests",
            "Servidor bloqueia IPs de datacenter (403 WAF); usar rede local",
            "Edições completas disponíveis como PDF via dosp.com.br",
        ],
    }

    log.info(f"  → Título: {titulo}")
    log.info(f"  → Total de links: {len(links)}")
    log.info(f"  → Seções encontradas: {len(secoes_info)}")
    return resultado


def coletar_lista_atos(tipo_ato: str) -> list[dict]:
    """
    Atividade 4 & 6 — Coleta a lista de atos de um determinado tipo.
    URL padrão: /listaatos.php?c=Avaré&s=<tipo_ato>

    Retorna lista de dicionários com os campos mínimos exigidos.
    """
    url = f"{BASE_URL}/listaatos.php?c={MUNICIPIO_PARAM}&s={tipo_ato}"
    log.info(f"Coletando lista de '{tipo_ato}': {url}")

    resp = fazer_requisicao(url)
    if not resp:
        log.error(f"Falha ao coletar '{tipo_ato}'")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # A tabela de atos tem colunas: Título | Data | Edição | Ano | Diário Oficial | Texto
    tabela = soup.find("table")
    if not tabela:
        log.warning(f"Nenhuma tabela encontrada para '{tipo_ato}'")
        return []

    publicacoes = []
    linhas = tabela.find_all("tr")[1:]   # pula o cabeçalho

    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) < 5:
            continue

        titulo_raw = colunas[0].get_text(strip=True)
        data_raw = colunas[1].get_text(strip=True)
        edicao_raw = colunas[2].get_text(strip=True)
        # ano_raw = colunas[3].get_text(strip=True)   # não usaremos diretamente

        # Links para edição completa e texto individual
        link_edicao_tag = colunas[4].find("a")
        link_texto_tag = colunas[5].find("a") if len(colunas) > 5 else None

        url_edicao = link_edicao_tag["href"] if link_edicao_tag else ""
        url_texto = link_texto_tag["href"] if link_texto_tag else ""

        # Converte data do formato DD/MM/AAAA para AAAA-MM-DD (ISO 8601)
        data_iso = converter_data(data_raw)

        # Inferir secretaria a partir do título (heurística simples)
        secretaria = inferir_secretaria(titulo_raw)

        publicacoes.append({
            "data_publicacao": data_iso,
            "numero_edicao": edicao_raw,
            "titulo_ato": titulo_raw,
            "tipo_ato": tipo_ato,
            "url_documento": url_edicao,
            "url_texto": url_texto,
            "secretaria": secretaria,
        })

    log.info(f"  → {len(publicacoes)} atos coletados para '{tipo_ato}'")
    return publicacoes


def converter_data(data_str: str) -> str:
    """Converte 'DD/MM/AAAA' → 'AAAA-MM-DD'. Retorna string original se falhar."""
    try:
        return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return data_str


def inferir_secretaria(titulo: str) -> str:
    """
    Heurística simples para inferir a secretaria a partir do título do ato.
    Será aprimorada na Etapa 2 com NLP.
    """
    titulo_lower = titulo.lower()
    mapeamento = {
        "saúde": "Secretaria de Saúde",
        "educação": "Secretaria de Educação",
        "educacao": "Secretaria de Educação",
        "finanças": "Secretaria de Finanças",
        "financas": "Secretaria de Finanças",
        "administração": "Secretaria de Administração",
        "administracao": "Secretaria de Administração",
        "obras": "Secretaria de Obras",
        "meio ambiente": "Secretaria de Meio Ambiente",
        "assistência": "Secretaria de Assistência Social",
        "assistencia": "Secretaria de Assistência Social",
        "cultura": "Secretaria de Cultura",
        "esporte": "Secretaria de Esporte",
        "transporte": "Secretaria de Transporte",
        "agricultura": "Secretaria de Agricultura",
    }
    for chave, secretaria in mapeamento.items():
        if chave in titulo_lower:
            return secretaria
    return "Não identificada"


# ─── Atividade 5: Diagnóstico de JavaScript dinâmico ──────────────────────────

def diagnosticar_javascript() -> dict:
    """
    Atividade 5 — Verifica se o site requer JavaScript para exibir conteúdo.
    Compara o conteúdo retornado por requests com o esperado via navegador.
    """
    url = f"{BASE_URL}/{MUNICIPIO}"
    resp = fazer_requisicao(url)
    if not resp:
        return {"requer_js": "indeterminado", "motivo": "Não foi possível acessar o site"}

    soup = BeautifulSoup(resp.text, "html.parser")

    # Verifica presença de elementos esperados
    tem_secoes = bool(soup.find_all("li"))
    tem_tabela_edicoes = bool(soup.find("table"))

    # A seção "Edições Veiculadas" aparece no HTML mas sem dados reais — indica JS
    texto_pagina = resp.text.lower()
    menciona_edicoes = "edições veiculadas" in texto_pagina or "edicoes veiculadas" in texto_pagina

    resultado = {
        "url_testada": url,
        "status_http": resp.status_code,
        "tamanho_html_bytes": len(resp.text),
        "tem_lista_secoes": tem_secoes,
        "tem_tabela_edicoes_na_home": tem_tabela_edicoes,
        "menciona_edicoes_veiculadas": menciona_edicoes,
        "requer_js_para_home": not tem_tabela_edicoes,
        "paginas_estaticas_funcionam": True,   # /listaatos.php não requer JS
        "ferramenta_recomendada": (
            "requests + BeautifulSoup para /listaatos.php | "
            "Playwright para a página principal (edições)"
        ),
        "decisao_final": (
            "Usar requests + BeautifulSoup para coletar os atos via /listaatos.php. "
            "A página principal usa JS dinâmico para listar edições, mas as "
            "páginas de listagem por tipo (/listaatos.php) retornam HTML completo "
            "e são suficientes para os objetivos da Etapa 1."
        ),
    }
    return resultado


# ─── Pipeline principal ────────────────────────────────────────────────────────

def executar_coleta() -> pd.DataFrame:
    """
    Pipeline completo da Etapa 1:
    1. Explora a página principal
    2. Diagnostica necessidade de JavaScript
    3. Coleta atos de todas as categorias definidas
    4. Salva CSV
    """
    log.info("=" * 60)
    log.info("DIÁRIO OFICIAL INTELIGENTE DE AVARÉ — ETAPA 1")
    log.info("Exploração e Coleta Automatizada")
    log.info("=" * 60)

    # ── Atividade 1: Exploração ──────────────────────────────────────────
    log.info("\n[ATIVIDADE 1] Explorando estrutura do site...")
    info_site = explorar_pagina_principal()
    for obs in info_site.get("observacoes", []):
        log.info(f"  • {obs}")

    # ── Atividade 5: Diagnóstico JS ──────────────────────────────────────
    log.info("\n[ATIVIDADE 5] Verificando necessidade de JavaScript...")
    diag = diagnosticar_javascript()
    log.info(f"  → Requer JS na home: {diag.get('requer_js_para_home')}")
    log.info(f"  → Decisão: {diag.get('decisao_final')}")

    # ── Atividade 4 & 6: Coleta dos atos ────────────────────────────────
    log.info("\n[ATIVIDADE 4/6] Iniciando coleta de publicações...")
    todas_publicacoes = []

    for tipo_ato in SECOES.keys():
        publicacoes = coletar_lista_atos(tipo_ato)
        todas_publicacoes.extend(publicacoes)
        time.sleep(1)   # respeita o servidor — não sobrecarregar

    if not todas_publicacoes:
        log.warning("Nenhuma publicação coletada. Verifique sua conexão de rede.")
        log.warning("IMPORTANTE: Execute a partir de uma rede local (não datacenter).")
        return pd.DataFrame()

    # ── Monta DataFrame e salva CSV ──────────────────────────────────────
    df = pd.DataFrame(todas_publicacoes)

    # Ordenar por data (mais recente primeiro)
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], errors="coerce")
    df = df.sort_values("data_publicacao", ascending=False)
    df["data_publicacao"] = df["data_publicacao"].dt.strftime("%Y-%m-%d")

    # Remove duplicatas (mesmo título + edição)
    df = df.drop_duplicates(subset=["titulo_ato", "numero_edicao"])

    # Salva
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    caminho_csv = OUTPUT_DIR / "diario_avare.csv"
    df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

    log.info("\n" + "=" * 60)
    log.info(f"✅ {len(df)} publicações salvas em: {caminho_csv}")
    log.info(f"   Colunas: {list(df.columns)}")
    log.info("=" * 60)
    print(df.head(10).to_string())

    return df


if __name__ == "__main__":
    df = executar_coleta()

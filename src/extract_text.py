# src/extract_text.py
# Responsavel: extrair texto de PDFs e HTML
# Etapa 2 — Extração, Limpeza e Estruturação

import pdfplumber
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ─── Cenário A: extração de PDF ───────────────────────────────────────────────

def baixar_pdf(url: str, destino: str) -> bool:
    """
    Baixa um PDF a partir de uma URL e salva localmente.
    Retorna True se o download foi bem-sucedido.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and b'%PDF' in r.content[:10]:
            Path(destino).parent.mkdir(parents=True, exist_ok=True)
            Path(destino).write_bytes(r.content)
            return True
        return False
    except Exception as e:
        print(f"[ERRO] Download falhou: {e}")
        return False


def extrair_de_pdf(caminho: str) -> str:
    """Extrai texto de um arquivo PDF local."""
    textos = []
    try:
        with pdfplumber.open(caminho) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    textos.append(t)
    except Exception as e:
        print(f"[ERRO] Falha ao abrir PDF {caminho}: {e}")
    return '\n'.join(textos)


# ─── Cenário B: extração de HTML ──────────────────────────────────────────────

def extrair_de_html(url: str) -> str:
    """Extrai texto de uma página HTML remota."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9'
    }
    try:
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code != 200:
            print(f"[AVISO] Status {r.status_code} para {url}")
            return ''
        soup = BeautifulSoup(r.text, 'html.parser')
        # Remove scripts, estilos e navegação
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        # Extrai o texto principal
        texto = soup.get_text(separator='\n', strip=True)
        return texto
    except Exception as e:
        print(f"[ERRO] Falha ao extrair HTML de {url}: {e}")
        return ''


# ─── Ponto de entrada — teste rápido ──────────────────────────────────────────

if __name__ == '__main__':
    # Teste com URL de texto individual do Diário Oficial de Avaré
    url_teste = 'https://www.dosp.com.br/leituratexto?p=MjYyMjIxMw=='
    print(f'Testando extração HTML: {url_teste}')
    texto = extrair_de_html(url_teste)
    print(f'Caracteres extraídos: {len(texto)}')
    print('Primeiros 500 caracteres:')
    print(texto[:500])

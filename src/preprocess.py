# src/preprocess.py
# Responsavel: limpeza e normalização dos textos
# Etapa 2 — Extração, Limpeza e Estruturação

import re
import unicodedata


def limpar_texto(texto: str) -> str:
    """
    Limpeza básica do texto extraído de PDF ou HTML:
    - Remove múltiplos espaços em branco
    - Remove múltiplas quebras de linha
    - Remove linhas com apenas números (números de página)
    - Remove caracteres de controle
    """
    # Remove múltiplos espaços em branco
    texto = re.sub(r'[ \t]+', ' ', texto)
    # Remove múltiplas quebras de linha
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    # Remove linhas com apenas números (números de página)
    texto = re.sub(r'^\s*\d+\s*$', '', texto, flags=re.MULTILINE)
    # Remove caracteres de controle
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', texto)
    # Remove espaços no início e fim
    texto = texto.strip()
    return texto


def normalizar_texto(texto: str) -> str:
    """
    Normalização adicional:
    - Converte acentos para forma NFC (padrão Unicode)
    - Remove traço duplo e variantes tipográficas
    ATENÇÃO: NÃO remove acentos, NÃO converte para minúsculas
    e NÃO remove stopwords — isso será feito na Etapa 3.
    """
    # Converte acentos para forma NFC (padrão Unicode)
    texto = unicodedata.normalize('NFC', texto)
    # Remove traço duplo e variantes
    texto = texto.replace('--', '-').replace('\u00a0', ' ')
    return texto


def processar(texto: str) -> str:
    """
    Aplica limpeza e normalização em sequência.
    Função principal a ser chamada pelo pipeline.
    """
    return normalizar_texto(limpar_texto(texto))


# ─── Ponto de entrada — teste rápido ─────────────────────────────────────────

if __name__ == '__main__':
    texto_sujo = '  Decreto 123  \n\n\n  Prefeitura de Avaré  \n 1 \n  Art. 1º --  resolve:\n\n\n\n'
    texto_limpo = processar(texto_sujo)
    print('Entrada:')
    print(repr(texto_sujo))
    print('\nSaída limpa:')
    print(repr(texto_limpo))

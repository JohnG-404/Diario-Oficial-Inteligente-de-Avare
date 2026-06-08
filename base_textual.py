import requests, pandas as pd, time
from pathlib import Path
from bs4 import BeautifulSoup
import re, unicodedata

# ── importa as funções dos scripts ──────────────────────────
from src.extract_text import extrair_de_html, baixar_pdf, extrair_de_pdf
from src.preprocess import processar

# ── carrega o CSV da Etapa 1 ────────────────────────────────
df_urls = pd.read_csv('data/diario_avare.csv')
print(f'{len(df_urls)} URLs carregadas')

registros = []

for i, row in df_urls.iterrows():
    print(f'[{i+1}/{len(df_urls)}] {row["titulo_ato"][:50]}')

    texto_bruto = ''

    # Tenta HTML primeiro (mais limpo)
    if pd.notna(row.get('url_texto')) and row['url_texto']:
        texto_bruto = extrair_de_html(row['url_texto'])

    # Se não tem url_texto, baixa o PDF
    elif pd.notna(row.get('url_documento')) and row['url_documento']:
        destino = f'data/raw/edicao_{row["numero_edicao"]}.pdf'
        if baixar_pdf(row['url_documento'], destino):
            texto_bruto = extrair_de_pdf(destino)

    # Aplica limpeza
    texto_limpo = processar(texto_bruto)

    registros.append({
        'id':              f'DOA-{i+1:03d}',
        'data_publicacao': row['data_publicacao'],
        'numero_edicao':   row['numero_edicao'],
        'tipo_ato':        row['tipo_ato'],
        'titulo':          row['titulo_ato'],
        'secretaria':      row.get('secretaria', ''),
        'texto':           texto_limpo,
        'url_original':    row.get('url_documento', ''),
        'rotulo':          ''   
    })

    time.sleep(1)  # respeita o servidor

# Salva base_textual.csv
Path('data/processed').mkdir(exist_ok=True)
df = pd.DataFrame(registros)
df.to_csv('data/processed/base_textual.csv', index=False, encoding='utf-8')
print(f'\n✅ {len(df)} registros salvos em data/processed/base_textual.csv')
print(df[['id','titulo','tipo_ato']].head(10).to_string())
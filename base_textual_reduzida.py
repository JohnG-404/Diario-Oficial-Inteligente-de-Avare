import time
import pandas as pd
from pathlib import Path

from src.extract_text import extrair_de_html, baixar_pdf, extrair_de_pdf
from src.preprocess import processar

# ── Configuração ──────────────────────────────────────────────────────────────
LIMITE_LINHAS = 50      # ajuste aqui: quantos registros processar (None = todos)
PAUSA_SEGUNDOS = 1       # pausa entre requisições para não sobrecarregar o servidor
# ─────────────────────────────────────────────────────────────────────────────

df_urls = pd.read_csv('data/diario_avare.csv')

if LIMITE_LINHAS is not None:
    df_urls = df_urls.head(LIMITE_LINHAS)

print(f'Processando {len(df_urls)} registros (limite={LIMITE_LINHAS})\n')

registros = []

for i, row in df_urls.iterrows():
    print(f'[{i+1}/{len(df_urls)}] {str(row["titulo_ato"])[:55]}')

    texto_bruto = ''

    # Tenta HTML primeiro (mais limpo — texto de um único ato)
    if pd.notna(row.get('url_texto')) and row['url_texto']:
        texto_bruto = extrair_de_html(row['url_texto'])

    # Se não tem url_texto, baixa o PDF da edição completa
    elif pd.notna(row.get('url_documento')) and row['url_documento']:
        destino = f'data/raw/edicao_{row["numero_edicao"]}.pdf'
        if baixar_pdf(row['url_documento'], destino):
            texto_bruto = extrair_de_pdf(destino)

    texto_limpo = processar(texto_bruto)

    if not texto_limpo:
        print('  ⚠️  texto vazio — PDF pode ser escaneado ou URL inacessível')

    registros.append({
        'id':              f'DOA-{len(registros)+1:03d}',
        'data_publicacao': row['data_publicacao'],
        'numero_edicao':   row['numero_edicao'],
        'tipo_ato':        row['tipo_ato'],
        'titulo':          row['titulo_ato'],
        'secretaria':      row.get('secretaria', ''),
        'texto':           texto_limpo,
        'url_original':    row.get('url_documento', ''),
        'rotulo':          ''
    })

    time.sleep(PAUSA_SEGUNDOS)

Path('data/processed').mkdir(exist_ok=True)
df = pd.DataFrame(registros)
df.to_csv('data/processed/base_textual_reduzida.csv', index=False, encoding='utf-8')

com_texto = (df['texto'].str.len() > 50).sum()
print(f'\n✅ {len(df)} registros salvos em data/processed/base_textual_reduzida.csv')
print(f'   Com texto extraído: {com_texto}/{len(df)}')
print(df[['id', 'titulo', 'tipo_ato']].to_string())

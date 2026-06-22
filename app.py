"""
app.py — Interface Web para o Classificador de Atos do Diário Oficial de Avaré

Modelo atual:
    Classes: lei, decreto, portaria

Uso:
    python app.py

Acesse:
    http://localhost:5000
"""

import json
from flask import Flask, render_template_string, request, jsonify
from src.inferencia import carregar_pipeline, classificar

app = Flask(__name__)

print("⏳ Carregando modelo...")
try:
    PIPELINE = carregar_pipeline()
    print("✅ Modelo carregado.")
except Exception as e:
    PIPELINE = None
    print(f"❌ Erro ao carregar modelo: {e}")


EXEMPLOS = [
    {
        "label": "Decreto",
        "texto": (
            "DECRETO Nº 8.742, DE 14 DE MAIO DE 2026. "
            "O PREFEITO MUNICIPAL DE AVARÉ, Estado de São Paulo, "
            "no uso de suas atribuições legais, DECRETA: "
            "Art. 1º Fica aberto Crédito Adicional Suplementar no Orçamento vigente."
        ),
    },
    {
        "label": "Lei",
        "texto": (
            "LEI Nº 3.457, DE 02 DE JUNHO DE 2026. "
            "Institui a Política Municipal de Transparência da Infraestrutura Escolar "
            "no Município de Avaré/SP e dá outras providências. "
            "Faço saber que a Câmara Municipal aprovou e eu sanciono e promulgo a seguinte Lei."
        ),
    },
    {
        "label": "Portaria",
        "texto": (
            "PORTARIA Nº 1.113/2026. "
            "O SECRETÁRIO MUNICIPAL, no uso de suas atribuições legais, RESOLVE: "
            "Art. 1º Designar a servidora Maria da Silva para exercer suas funções junto à unidade administrativa."
        ),
    },
]


TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Diário Oficial Inteligente de Avaré</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">

  <style>
    :root {
      --cor-primaria: #1a3c5e;
      --cor-acento: #2e86c1;
    }

    body {
      background: #f4f6f9;
      font-family: 'Segoe UI', sans-serif;
    }

    .navbar-brand {
      font-weight: 700;
      letter-spacing: .5px;
    }

    .hero {
      background: linear-gradient(135deg, var(--cor-primaria), var(--cor-acento));
      color: #fff;
      padding: 2rem 0 1.5rem;
      margin-bottom: 2rem;
    }

    .hero h1 {
      font-size: 1.8rem;
      font-weight: 700;
    }

    .card-resultado {
      border-left: 5px solid var(--cor-acento);
    }

    textarea {
      resize: vertical;
      min-height: 150px;
    }

    #spinner {
      display: none;
    }

    footer {
      color: #888;
      font-size: .82rem;
      border-top: 1px solid #e0e0e0;
      padding-top: 1rem;
    }
  </style>
</head>

<body>

<nav class="navbar navbar-dark" style="background: var(--cor-primaria);">
  <div class="container">
    <span class="navbar-brand">🏛️ Diário Oficial Inteligente — Avaré/SP</span>
    <span class="text-white-50 small">Redes Neurais · NLP · PyTorch</span>
  </div>
</nav>

<div class="hero">
  <div class="container">
    <h1>Classificador de Leis, Decretos e Portarias</h1>
    <p>Cole o texto de uma publicação do Diário Oficial e o modelo identificará automaticamente sua classe.</p>
  </div>
</div>

<div class="container mb-5">
  <div class="row g-4">

    <div class="col-lg-7">
      <div class="card shadow-sm">
        <div class="card-body">
          <label class="form-label fw-semibold" for="texto">Texto do ato</label>

          <textarea class="form-control mb-2" id="texto" rows="6"
            placeholder="Cole aqui o texto completo ou um trecho do ato oficial..."></textarea>

          <div class="mb-3">
            <small class="text-muted me-2">Exemplos:</small>
            {% for ex in exemplos %}
            <button class="btn btn-outline-secondary btn-sm me-1 mb-1"
                    onclick="usarExemplo({{ loop.index0 }})">
              {{ ex.label }}
            </button>
            {% endfor %}
          </div>

          <button class="btn btn-primary px-4" onclick="classificarTexto()">
            <span id="spinner" class="spinner-border spinner-border-sm me-2"></span>
            🔍 Classificar
          </button>

          <button class="btn btn-outline-secondary ms-2" onclick="limpar()">Limpar</button>
        </div>
      </div>
    </div>

    <div class="col-lg-5">
      <div id="resultado" style="display:none;">
        <div class="card shadow-sm card-resultado mb-3">
          <div class="card-body text-center py-4">
            <div style="font-size: 2.5rem;" id="res-icone">📄</div>

            <h5 class="fw-bold mt-2 mb-1" id="res-nome">—</h5>

            <span class="badge bg-primary" id="res-classe">—</span>

            <div class="mt-3">
              <small class="text-muted">Confiança</small>

              <div class="progress mt-1" style="height:18px;">
                <div id="barra-principal" class="progress-bar"
                     role="progressbar" style="width: 0%"></div>
              </div>

              <strong id="res-confianca" class="fs-5">—</strong>
            </div>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-header bg-white fw-semibold">Top-3 probabilidades</div>
          <ul class="list-group list-group-flush" id="ranking-lista"></ul>
        </div>

        <small class="text-muted mt-2 d-block" id="info-tokens"></small>
      </div>

      <div id="placeholder" class="text-center text-muted py-5">
        <div style="font-size: 3rem">📄</div>
        <p>Cole um texto e clique em <strong>Classificar</strong></p>
      </div>
    </div>
  </div>

  <div class="row mt-4">
    <div class="col">
      <div class="card shadow-sm">
        <div class="card-header bg-white fw-semibold">ℹ️ Sobre o modelo</div>

        <div class="card-body">
          <div class="row text-center">
            <div class="col-md-3 mb-2">
              <div class="fw-bold text-primary fs-5">EmbedAvg</div>
              <small class="text-muted">Arquitetura</small>
            </div>

            <div class="col-md-3 mb-2">
              <div class="fw-bold text-primary fs-5">{{ vocab_size }}</div>
              <small class="text-muted">Tokens no vocabulário</small>
            </div>

            <div class="col-md-3 mb-2">
              <div class="fw-bold text-primary fs-5">{{ num_classes }}</div>
              <small class="text-muted">Classes</small>
            </div>

            <div class="col-md-3 mb-2">
              <div class="fw-bold text-primary fs-5">600</div>
              <small class="text-muted">Amostras rotuladas</small>
            </div>
          </div>

          <hr>

          <p class="mb-1 small text-muted">
            <strong>Classes:</strong>
            Lei · Decreto · Portaria
          </p>

          <p class="mb-0 small text-muted">
            O modelo foi treinado com publicações reais do Diário Oficial de Avaré, usando tokenização,
            vocabulário próprio e uma rede neural simples com embeddings.
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<footer class="container mb-4 text-center">
  Projeto de Redes Neurais e IA Aplicada — Diário Oficial Inteligente de Avaré
</footer>

<script>
  const exemplos = {{ exemplos | tojson }};

  function usarExemplo(idx) {
    document.getElementById('texto').value = exemplos[idx].texto;
  }

  async function classificarTexto() {
    const texto = document.getElementById('texto').value.trim();

    if (!texto) {
      alert('Cole um texto antes de classificar.');
      return;
    }

    document.getElementById('spinner').style.display = 'inline-block';
    document.getElementById('placeholder').style.display = 'none';
    document.getElementById('resultado').style.display = 'none';

    try {
      const resp = await fetch('/classificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto })
      });

      const data = await resp.json();

      if (data.erro) {
        alert('Erro: ' + data.erro);
        document.getElementById('resultado').style.display = 'none';
        document.getElementById('placeholder').style.display = 'block';
        return;
      }

      const nomes = {
        'lei': 'Lei Municipal',
        'decreto': 'Decreto Municipal',
        'portaria': 'Portaria Administrativa'
      };

      const icones = {
        'lei': '⚖️',
        'decreto': '📜',
        'portaria': '📋'
      };

      document.getElementById('res-icone').textContent = icones[data.classe] || '📄';
      document.getElementById('res-nome').textContent = nomes[data.classe] || data.nome || data.classe;
      document.getElementById('res-classe').textContent = data.classe;

      const pct = (data.confianca * 100).toFixed(1);

      document.getElementById('res-confianca').textContent = pct + '%';

      const barra = document.getElementById('barra-principal');
      barra.style.width = pct + '%';
      barra.className = 'progress-bar ' +
        (data.confianca >= .7 ? 'bg-success' : data.confianca >= .5 ? 'bg-warning' : 'bg-danger');

      const lista = document.getElementById('ranking-lista');
      lista.innerHTML = '';

      data.ranking.forEach((r, i) => {
        const pctR = (r.confianca * 100).toFixed(1);
        const nomeClasse = nomes[r.classe] || r.nome || r.classe;
        const iconeClasse = icones[r.classe] || '📄';

        lista.innerHTML += `
          <li class="list-group-item py-2">
            <div class="d-flex justify-content-between mb-1">
              <small>${i + 1}. ${iconeClasse} ${nomeClasse}</small>
              <small class="fw-bold">${pctR}%</small>
            </div>
            <div class="progress" style="height:8px;">
              <div class="progress-bar bg-info" style="width:${pctR}%"></div>
            </div>
          </li>`;
      });

      document.getElementById('info-tokens').textContent =
        `Tokens reconhecidos: ${data.tokens_usados}/${data.tokens_total}`;

      document.getElementById('resultado').style.display = 'block';

    } catch (e) {
      alert('Erro de conexão: ' + e.message);
      document.getElementById('placeholder').style.display = 'block';
    } finally {
      document.getElementById('spinner').style.display = 'none';
    }
  }

  function limpar() {
    document.getElementById('texto').value = '';
    document.getElementById('resultado').style.display = 'none';
    document.getElementById('placeholder').style.display = 'block';
  }
</script>

</body>
</html>
"""


@app.route("/")
def index():
    if PIPELINE is None:
        return "<h1>Erro</h1><p>Modelo não carregado. Verifique models/modelo.pt.</p>", 500

    return render_template_string(
        TEMPLATE,
        exemplos=EXEMPLOS,
        vocab_size=len(PIPELINE["vocab"]),
        num_classes=len(PIPELINE["label_map"]),
    )


@app.route("/classificar", methods=["POST"])
def rota_classificar():
    if PIPELINE is None:
        return jsonify({"erro": "Modelo não carregado."}), 500

    dados = request.get_json(force=True)
    texto = dados.get("texto", "").strip()

    if not texto:
        return jsonify({"erro": "Texto vazio."}), 400

    try:
        resultado = classificar(texto, PIPELINE)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "ok" if PIPELINE else "erro",
        "modelo_carregado": PIPELINE is not None,
        "vocab_size": len(PIPELINE["vocab"]) if PIPELINE else 0,
        "num_classes": len(PIPELINE["label_map"]) if PIPELINE else 0,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
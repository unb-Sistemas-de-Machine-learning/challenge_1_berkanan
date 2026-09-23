"""
streamlit_app.py — Frontend do Fact-Checker de Diabetes e Nutrição (MVP).

Consome a API FastAPI via HTTP. Não depende do modelo local.

Configuração:
    - Localmente: API_URL=http://localhost:8000 streamlit run streamlit_app.py
    - Em produção (Streamlit Cloud): configura a variável de ambiente API_URL
      nas Secrets do Streamlit Cloud apontando para o URL do Render.
"""

import os

import requests
import streamlit as st

# --------------------------------------------------------------------------- #
# Configuração                                                                 #
# --------------------------------------------------------------------------- #
API_URL = os.getenv("API_URL", "http://localhost:8000")
PREDICT_URL = f"{API_URL}/predict"
HEALTH_URL = f"{API_URL}/health"

st.set_page_config(
    page_title="Fact-Checker Diabetes e Nutrição",
    page_icon="🩺",
    layout="centered",
)

# --------------------------------------------------------------------------- #
# Layout                                                                       #
# --------------------------------------------------------------------------- #
st.title("🩺 Fact-Checker — Diabetes e Nutrição")
st.caption(
    "Verifique se uma afirmação sobre alimentação e diabetes é **FAKE** ou **REAL** "
    "com base em evidências científicas."
)
st.divider()

# Verifica se a API está no ar
try:
    health = requests.get(HEALTH_URL, timeout=5).json()
    st.sidebar.success(f"✅ API conectada\n\n**Modelo:** {health.get('model')}\n\n**Threshold:** {health.get('threshold')}")
except Exception:
    st.sidebar.error("❌ API inacessível — verifique se está rodando.")

# Campo de entrada
user_text = st.text_area(
    "Digite uma afirmação sobre diabetes ou nutrição:",
    placeholder="Ex: Canela cura diabetes tipo 2",
    height=120,
)

col1, col2 = st.columns([1, 3])
with col1:
    verificar = st.button("🔍 Verificar", type="primary", use_container_width=True)

# --------------------------------------------------------------------------- #
# Chamada à API e resultado                                                    #
# --------------------------------------------------------------------------- #
if verificar:
    if not user_text.strip():
        st.warning("Por favor, digite uma afirmação antes de verificar.")
    else:
        with st.spinner("Analisando..."):
            try:
                resp = requests.post(
                    PREDICT_URL,
                    json={"text": user_text.strip()},
                    timeout=10,
                )
                resp.raise_for_status()
                result = resp.json()

                label = result["label"]
                p_fake = result["p_fake"]
                threshold = result["threshold"]

                st.divider()

                if label == "FAKE":
                    st.error(f"## ⚠️ FAKE NEWS detectada")
                    st.markdown(
                        f"Esta afirmação apresenta características de desinformação "
                        f"sobre diabetes ou nutrição."
                    )
                else:
                    st.success(f"## ✅ Informação parece REAL")
                    st.markdown(
                        f"Esta afirmação está alinhada com o padrão de informações "
                        f"verificadas sobre diabetes ou nutrição."
                    )

                st.divider()
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Classificação", label)
                col_b.metric("Prob. FAKE", f"{p_fake:.1%}")
                col_c.metric("Threshold", f"{threshold:.2f}")

                st.progress(p_fake, text=f"Probabilidade de ser FAKE: {p_fake:.1%}")

                with st.expander("ℹ️ Como interpretar"):
                    st.markdown(
                        f"- O modelo calcula a probabilidade de a afirmação ser **FAKE** (`p_fake`).\n"
                        f"- Se `p_fake ≥ {threshold}` (threshold calibrado), a afirmação é marcada como **FAKE**.\n"
                        f"- O threshold foi calibrado para maximizar o **recall** da classe FAKE, "
                        f"minimizando falsos negativos (o erro mais perigoso neste contexto).\n"
                        f"- **⚠️ Este é um protótipo acadêmico.** Não substitui orientação médica profissional."
                    )

            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se ela está rodando.")
            except requests.exceptions.Timeout:
                st.error("⏱️ A API demorou demais para responder. Tente novamente.")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

# --------------------------------------------------------------------------- #
# Footer                                                                       #
# --------------------------------------------------------------------------- #
st.divider()
st.caption(
    "🎓 Projeto acadêmico — Equipe Berkanan | Sistemas de Machine Learning 2026/02 | UnB  \n"
    "Modelo: MultinomialNB + TF-IDF | Dataset: afirmações sobre diabetes/nutrição em português"
)

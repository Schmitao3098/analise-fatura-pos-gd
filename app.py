import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Consumo – Pós Energia Solar", layout="centered")
st.title("🔍 Consumo – Pós Energia Solar")
st.markdown("Envie sua fatura (PDF) da Copel e informe a geração do sistema no período para análise completa.")

# Upload da fatura PDF
uploaded_file = st.file_uploader("📄 Enviar fatura da Copel (PDF):", type=["pdf"])

# Funções auxiliares para extração dos dados do PDF
def extrair_texto_pdf(file):
    texto = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def extrair_dados_fatura(texto):
    dados = {}

    # Datas de leitura
    match_datas = re.findall(r"(\d{2}/\d{2}/\d{4})", texto)
    if len(match_datas) >= 2:
        dados["leitura_inicio"] = match_datas[0]
        dados["leitura_fim"] = match_datas[1]

    # Consumo
    match_consumo = re.search(r"ENERGIA ELET CONSUMO\s+kWh\s+(\d+)", texto)
    dados["consumo"] = int(match_consumo.group(1)) if match_consumo else 0

    # Injeção TE
    match_te = re.search(r"ENERGIA INJETADA TE.*?kWh\s+(-?\d+)", texto)
    injetada_te = int(match_te.group(1)) if match_te else 0

    # Injeção TUSD
    match_tusd = re.search(r"ENERGIA INJETADA TUSD.*?kWh\s+(-?\d+)", texto)
    injetada_tusd = int(match_tusd.group(1)) if match_tusd else 0

    dados["injetada"] = abs(injetada_te + injetada_tusd)

    return dados

# Lógica principal do app
if uploaded_file:
    texto_extraido = extrair_texto_pdf(uploaded_file)
    dados = extrair_dados_fatura(texto_extraido)

    with st.container():
        st.success(f"📅 Período da leitura: {dados.get('leitura_inicio', 'N/A')} a {dados.get('leitura_fim', 'N/A')}")

    # Campo para informar a geração real
    geracao_manual = st.number_input("🔢 Informe a geração total do sistema no período (kWh):", min_value=0.0, step=0.1, format="%.2f")

    if geracao_manual > 0:
        consumo_rede = dados["consumo"]
        energia_injetada = dados["injetada"]
        geracao_total = geracao_manual
        eficiencia_local = ((geracao_total - energia_injetada) / geracao_total) * 100 if geracao_total else 0
        eficiencia_total = (geracao_total / consumo_rede) * 100 if consumo_rede else 0
        creditos = geracao_total - consumo_rede

        st.markdown("---")
        st.subheader("📊 Resultados da Análise")
        st.write(f"📥 Consumo da rede (Copel): **{consumo_rede} kWh**")
        st.write(f"⚡ Energia injetada (créditos): **{energia_injetada} kWh**")
        st.write(f"🌞 Geração real informada: **{geracao_total} kWh**")
        st.write(f"🎯 Aproveitamento local da geração: **{eficiencia_local:.1f}%**")
        st.write(f"📈 Eficiência total da geração: **{eficiencia_total:.1f}%**")
        st.write(f"💳 Estimativa de crédito acumulado: **{creditos:.2f} kWh**")

        st.subheader("🧠 Interpretação")
        if creditos > 0:
            st.info("🔋 Muitos créditos sobrando: pode estar gerando mais do que consome.")
        elif creditos < 0:
            st.warning("⚠️ Geração insuficiente: pode haver necessidade de redimensionamento.")
        else:
            st.success("✅ Geração equilibrada com o consumo.")

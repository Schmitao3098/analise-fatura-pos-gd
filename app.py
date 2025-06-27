import streamlit as st
import fitz  # PyMuPDF
import re
from datetime import datetime

st.set_page_config(page_title="Consumo – Pós Energia Solar", layout="wide")
st.title("🔍 Consumo – Pós Energia Solar")

# Função para extrair texto do PDF
def extrair_texto_pdf(pdf_file):
    texto = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

# Função para extrair datas e energia da fatura
def extrair_dados_fatura(texto):
    dados = {}

    datas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', texto)
    if len(datas) >= 2:
        try:
            dados["leitura_inicio"] = datetime.strptime(datas[0], "%d/%m/%Y").date()
            dados["leitura_fim"] = datetime.strptime(datas[1], "%d/%m/%Y").date()
        except:
            dados["leitura_inicio"] = None
            dados["leitura_fim"] = None
    else:
        dados["leitura_inicio"] = None
        dados["leitura_fim"] = None

    # Energia injetada (pode ser negativa na fatura)
    match = re.search(r'ENERGIA INJETADA.*?(-?\d{1,4})\s*kWh', texto, re.IGNORECASE)
    if match:
        try:
            dados["energia_injetada"] = abs(int(match.group(1)))
        except:
            dados["energia_injetada"] = 0
    else:
        dados["energia_injetada"] = 0

    return dados

# Upload da fatura
fatura = st.file_uploader("📄 Envie a fatura (PDF):", type=["pdf"])

if fatura:
    texto = extrair_texto_pdf(fatura)
    st.subheader("📑 Texto extraído da fatura:")
    with st.expander("🔍 Ver texto"):
        st.text(texto)

    dados = extrair_dados_fatura(texto)

    leitura_inicio = st.date_input("📆 Data de leitura anterior:", value=dados["leitura_inicio"])
    leitura_fim = st.date_input("📆 Data de leitura atual:", value=dados["leitura_fim"])

    energia_injetada = dados["energia_injetada"]
    st.info(f"⚡ Energia injetada identificada: **{energia_injetada} kWh**")

    # Entrada manual da geração
    st.markdown("### ☀️ Informe manualmente a geração solar do período:")
    geracao_total = st.number_input("Geração total no período (kWh):", min_value=0.0, value=0.0, step=0.01)

    # Cálculos
    consumo_estimado = energia_injetada  # ou outro modelo se desejar
    eficiencia_uso = (consumo_estimado / geracao_total) * 100 if geracao_total else 0
    desempenho_meta = (geracao_total / consumo_estimado) * 100 if consumo_estimado else 0

    # Resultados
    st.markdown("## 📊 Resultados")
    st.write(f"📅 Período: {leitura_inicio} até {leitura_fim}")
    st.write(f"🌞 Geração informada: **{geracao_total} kWh**")
    st.write(f"⚡ Energia injetada na rede: **{energia_injetada} kWh**")
    st.write(f"🔥 Consumo estimado: **{consumo_estimado} kWh**")
    st.write(f"📈 Eficiência de uso da geração: **{eficiencia_uso:.2f}%**")
    st.write(f"🎯 Desempenho da geração vs. meta: **{desempenho_meta:.2f}%**")

    # Sugestões
    st.markdown("## 💡 Sugestões")
    if geracao_total == 0:
        st.warning("⚠️ Geração zerada: verificar o sistema ou erro no lançamento.")
    elif eficiencia_uso < 30:
        st.info("😬 Baixa eficiência de uso: pode haver subutilização da geração.")
    if desempenho_meta < 70:
        st.info("💡 Baixo desempenho: avaliar dimensionamento do sistema.")
    if energia_injetada > consumo_estimado * 0.8:
        st.info("🌞 Alta injeção na rede: consumo local pode estar baixo.")

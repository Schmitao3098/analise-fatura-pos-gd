import streamlit as st
import fitz  # PyMuPDF
import re
from datetime import datetime

st.set_page_config(page_title="Consumo – Pós Energia Solar", layout="centered")
st.title("🔎 Consumo – Pós Energia Solar")

# Upload da fatura PDF
uploaded_fatura = st.file_uploader("📄 Envie a fatura (PDF):", type=["pdf"])
texto_extraido = ""

def extrair_texto_fatura(pdf_file):
    texto = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def extrair_dados_fatura(texto):
    # Datas
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
    data_inicio, data_fim = None, None
    if len(datas) >= 2:
        data_inicio = datas[0]
        data_fim = datas[1]

    # Energia injetada (padrão Copel: "ENERGIA INJETADA" seguido por números com vírgula ou ponto)
    inj_match = re.findall(r"ENERGIA INJETADA.*?[-–]?(\d+[\.,]?\d*)", texto.upper())
    energia_injetada = float(inj_match[0].replace(',', '.')) if inj_match else 0.0

    return data_inicio, data_fim, energia_injetada

# === PROCESSAMENTO DA FATURA ===
if uploaded_fatura:
    texto_extraido = extrair_texto_fatura(uploaded_fatura)
    data_inicio, data_fim, energia_injetada = extrair_dados_fatura(texto_extraido)

    st.subheader("📄 Texto extraído da fatura:")
    with st.expander("Ver texto"):
        st.text(texto_extraido)

    st.write("📅 **Data de leitura anterior:**", data_inicio or "Não encontrada")
    st.write("📅 **Data de leitura atual:**", data_fim or "Não encontrada")
    st.write("⚡ **Energia injetada identificada:**", f"{energia_injetada} kWh")

    # Entrada manual da geração solar
    st.subheader("🌞 Informe manualmente a geração solar do período:")
    geracao = st.number_input("Geração total no período (kWh):", min_value=0.0, step=1.0)

    # Resultados
    if geracao > 0:
        st.subheader("📊 Resultados")

        dias = (datetime.strptime(data_fim, "%d/%m/%Y") - datetime.strptime(data_inicio, "%d/%m/%Y")).days if data_inicio and data_fim else 30
        consumo_estimado = round(geracao - energia_injetada, 2)
        eficiencia = round(((geracao - energia_injetada) / geracao) * 100, 2) if geracao else 0
        desempenho = round((geracao / 2850) * 100, 2)  # Meta hipotética de 2850 kWh

        st.write("📆 Período:", f"{data_inicio} até {data_fim}")
        st.write("🌞 Geração informada:", f"{geracao:.1f} kWh")
        st.write("⚡ Energia injetada na rede:", f"{energia_injetada:.1f} kWh")
        st.write("🔥 Consumo estimado:", f"{consumo_estimado:.1f} kWh")
        st.write("📈 Eficiência de uso da geração:", f"{eficiencia:.2f}%")
        st.write("🎯 Desempenho da geração vs. meta:", f"{desempenho:.2f}%")

        # Sugestões
        st.subheader("💡 Sugestões")
        if eficiencia < 50:
            st.info("🤔 Baixa eficiência de uso: pode haver subutilização da geração.")
        if desempenho < 70:
            st.warning("📉 Baixo desempenho: avaliar dimensionamento do sistema.")
        if energia_injetada > (geracao * 0.5):
            st.warning("🔁 Alta injeção na rede: consumo local está baixo, considerar redimensionar.")

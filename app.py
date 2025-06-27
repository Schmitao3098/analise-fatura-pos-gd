import streamlit as st
import pandas as pd
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

    # Extrair datas
    datas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', texto)
    if len(datas) >= 2:
        try:
            dados["leitura_inicio"] = datetime.strptime(datas[0], "%d/%m/%Y").date()
            dados["leitura_fim"] = datetime.strptime(datas[1], "%d/%m/%Y").date()
        except ValueError:
            dados["leitura_inicio"] = None
            dados["leitura_fim"] = None
    else:
        dados["leitura_inicio"] = None
        dados["leitura_fim"] = None

    # Energia injetada
    match_injetada = re.search(r'ENERGIA INJETADA.*?(-?\d{1,4})\s*kWh', texto, re.IGNORECASE)
    if match_injetada:
        try:
            dados["energia_injetada"] = abs(int(match_injetada.group(1)))
        except:
            dados["energia_injetada"] = 0
    else:
        dados["energia_injetada"] = 0

    return dados

# Upload de arquivos
fatura = st.file_uploader("📄 Envie a fatura (PDF):", type=["pdf"])
relatorios = st.file_uploader("📊 Envie dois relatórios de geração (XLS/XLSX):", type=["xls", "xlsx"], accept_multiple_files=True)

# Processar fatura
if fatura:
    texto = extrair_texto_pdf(fatura)
    st.subheader("📄 Texto extraído da fatura:")
    with st.expander("Ver texto extraído"):
        st.text(texto)

    dados_fatura = extrair_dados_fatura(texto)

    # Datas detectadas
    st.success(f"📅 Período detectado: {dados_fatura['leitura_inicio']} a {dados_fatura['leitura_fim']}")

    # Datas editáveis
    leitura_inicio = st.date_input("📅 Data da leitura anterior (início):", value=dados_fatura["leitura_inicio"])
    leitura_fim = st.date_input("📅 Data da leitura atual (fim):", value=dados_fatura["leitura_fim"])

    # Geração solar (manual)
    st.markdown("### 🔢 Insira a geração solar no período informado:")
    geracao_total = st.number_input("Geração total no período (kWh):", min_value=0.0, value=0.0, step=0.01)

    # Energia injetada na rede
    energia_injetada = dados_fatura["energia_injetada"]

    # Cálculos
    consumo_estimado = energia_injetada  # Ajustar se necessário
    eficiencia_uso = (consumo_estimado / geracao_total) * 100 if geracao_total else 0
    desempenho_vs_meta = (geracao_total / consumo_estimado) * 100 if consumo_estimado else 0

    st.markdown("## 📊 Resultados")
    st.write(f"📆 **Período informado:** {leitura_inicio} a {leitura_fim}")
    st.write(f"🌞 **Geração total:** {geracao_total} kWh")
    st.write(f"⚡ **Energia injetada na rede:** {energia_injetada} kWh")
    st.write(f"🔥 **Consumo estimado:** {consumo_estimado} kWh")
    st.write(f"📈 **Eficiência de uso da geração:** {eficiencia_uso:.2f}%")
    st.write(f"🎯 **Desempenho da geração vs. meta:** {desempenho_vs_meta:.2f}%")

    # Sugestões
    st.markdown("## 💡 Sugestões")
    sugestoes = []

    if geracao_total == 0:
        sugestoes.append("⚠️ Geração abaixo do esperado: verificar sombreamentos ou falhas no sistema.")
    if eficiencia_uso < 30:
        sugestoes.append("😬 Baixa eficiência de uso: pode haver subutilização da geração.")
    if desempenho_vs_meta < 50 and geracao_total > 0:
        sugestoes.append("💡 Baixo desempenho de geração: possível problema de dimensionamento.")
    if energia_injetada > consumo_estimado * 0.8:
        sugestoes.append("🌞 Alta injeção na rede: consumo local está baixo, considerar redimensionar.")

    for s in sugestoes:
        st.info(s)

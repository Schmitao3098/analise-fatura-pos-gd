import streamlit as st
import fitz  # PyMuPDF
import re
from datetime import datetime
import pandas as pd

st.title("🔍 Consumo – Pós Energia Solar")

# ======== Uploads ==========
fatura = st.file_uploader("📄 Envie a fatura (PDF):", type="pdf")

# ========== Extrair texto da fatura ==========
def extrair_texto_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()
    return texto

# ========== Extrair datas de leitura ==========
def encontrar_datas(texto):
    padrao = r"(\d{2}/\d{2}/\d{4})"
    datas = re.findall(padrao, texto)
    if len(datas) >= 2:
        inicio = datetime.strptime(datas[0], "%d/%m/%Y").date()
        fim = datetime.strptime(datas[1], "%d/%m/%Y").date()
        return inicio, fim
    return None, None

# ========== Extrair energia injetada ==========
def extrair_injetada(texto):
    padrao = r"ENERGIA INJETADA.*?(\d+)"
    match = re.findall(padrao, texto)
    if match:
        return int(match[0])
    return 0

# ========== Processar Fatura ==========
if fatura:
    texto_fatura = extrair_texto_pdf(fatura)
    st.subheader("📑 Texto extraído da fatura:")
    st.text(texto_fatura)

    data_inicio, data_fim = encontrar_datas(texto_fatura)
    energia_injetada = extrair_injetada(texto_fatura)

    if data_inicio and data_fim:
        st.success(f"📅 Período detectado: {data_inicio} a {data_fim}")
    else:
        st.warning("⚠️ Não foi possível detectar datas automaticamente.")

    # Dados manuais (caso extração falhe)
    data_inicio = st.date_input("📆 Data da leitura anterior (início):", value=data_inicio or datetime.today())
    data_fim = st.date_input("📆 Data da leitura atual (fim):", value=data_fim or datetime.today())

    # Entrada manual da geração no período
    st.subheader("🔢 Insira a geração solar no período informado:")
    geracao_total = st.number_input("Geração total no período (kWh):", min_value=0.0, step=0.1)

    # Resultado
    dias_periodo = (data_fim - data_inicio).days or 1
    consumo_estimado = energia_injetada  # suposição simplificada
    eficiencia = 0 if geracao_total == 0 else consumo_estimado / geracao_total * 100
    desempenho = 0 if consumo_estimado == 0 else geracao_total / consumo_estimado * 100

    # ====== Resultados ======
    st.header("📊 Resultados")
    st.markdown(f"📆 **Período informado:** {data_inicio} a {data_fim}")
    st.markdown(f"☀️ **Geração total:** {geracao_total:.1f} kWh")
    st.markdown(f"⚡ **Energia injetada na rede:** {energia_injetada:.1f} kWh")
    st.markdown(f"📉 **Consumo estimado:** {consumo_estimado:.1f} kWh")
    st.markdown(f"📈 **Eficiência de uso da geração:** {eficiencia:.2f}%")
    st.markdown(f"🎯 **Desempenho da geração vs. meta:** {desempenho:.2f}%")

    # ====== Sugestões ======
    st.subheader("💡 Sugestões")
    if geracao_total == 0:
        st.warning("⚠️ Geração zerada: verificar falhas ou sombreamento.")
    elif eficiencia < 20:
        st.info("🧊 Baixa eficiência: pode haver subutilização.")
    elif desempenho < 50:
        st.info("🔋 Geração abaixo do esperado: pode ser problema de dimensionamento.")

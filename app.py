import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
from datetime import datetime

st.set_page_config(layout="wide")

# ---------- FUNÇÕES UTILITÁRIAS ----------

def extrair_texto_pdf(arquivo_pdf):
    with fitz.open(stream=arquivo_pdf.read(), filetype="pdf") as doc:
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
    return texto

def extrair_datas(texto):
    padrao_datas = re.findall(r"(\d{2}/\d{2}/\d{4})", texto)
    if len(padrao_datas) >= 2:
        try:
            data_inicio = datetime.strptime(padrao_datas[0], "%d/%m/%Y")
            data_fim = datetime.strptime(padrao_datas[1], "%d/%m/%Y")
            return data_inicio, data_fim
        except:
            return None, None
    return None, None

def extrair_valor_por_regex(texto, label):
    padrao = re.compile(fr"{label}[^\n]*\n?(-?\d+)", re.IGNORECASE)
    match = padrao.search(texto)
    if match:
        return abs(int(match.group(1)))
    return 0

def processar_planilha(planilha, data_inicio, data_fim):
    try:
        df = pd.read_excel(planilha)
        df.columns = df.columns.str.strip()  # limpa espaços

        # Identificar colunas relevantes
        col_data = next((col for col in df.columns if 'time' in col.lower()), None)
        col_geracao = next((col for col in df.columns if 'yield' in col.lower() or 'geracao' in col.lower()), None)

        if not col_data or not col_geracao:
            return 0.0

        df[col_data] = pd.to_datetime(df[col_data], errors='coerce')
        mask = (df[col_data] >= data_inicio) & (df[col_data] <= data_fim)
        total = df.loc[mask, col_geracao].sum()
        return round(total, 2)
    except Exception as e:
        st.warning(f"Erro ao processar planilha: {e}")
        return 0.0

# ---------- INTERFACE PRINCIPAL ----------

st.title("🔌 Consumo - Pós Energia Solar")

# Upload de arquivos
fatura = st.file_uploader("📄 Enviar fatura (PDF):", type="pdf")
planilhas = st.file_uploader("📊 Enviar dois relatórios de geração (XLSX):", type=["xls", "xlsx"], accept_multiple_files=True)

if fatura and len(planilhas) == 2:
    texto = extrair_texto_pdf(fatura)
    st.subheader("📋 Texto extraído da fatura:")
    st.text_area("Texto:", texto, height=250)

    data_inicio, data_fim = extrair_datas(texto)

    # Exibe datas extraídas
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("📅 Data da leitura anterior (início do período):", value=data_inicio)
    with col2:
        data_fim = st.date_input("📅 Data da leitura atual (fim do período):", value=data_fim)

    # Dados da fatura (usando regex)
    consumo_rede = extrair_valor_por_regex(texto, "ENERGIA ELET CONSUMO")
    energia_injetada = extrair_valor_por_regex(texto, "ENERGIA INJETADA")
    creditos = extrair_valor_por_regex(texto, "Saldo.*?Todos os Períodos")

    # Processa planilhas de geração
    geracao_total = sum([processar_planilha(p, data_inicio, data_fim) for p in planilhas])
    consumo_local = max(geracao_total - energia_injetada, 0)
    consumo_total_estimado = consumo_local + consumo_rede

    eficiencia = (consumo_local / geracao_total) * 100 if geracao_total > 0 else 0
    desempenho = (geracao_total / consumo_total_estimado) * 100 if consumo_total_estimado > 0 else 0

    # ---------- EXIBIÇÃO DOS RESULTADOS ----------
    st.header("📊 Resultados")

    st.markdown(f"📅 **Período informado:** {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    st.markdown(f"🌞 **Geração total no período:** {geracao_total} kWh")
    st.markdown(f"⚡ **Consumo da rede:** {consumo_rede} kWh")
    st.markdown(f"🔌 **Energia injetada na rede:** {energia_injetada} kWh")
    st.markdown(f"💳 **Créditos acumulados:** {creditos} kWh")
    st.markdown(f"📈 **Eficiência de uso da geração:** {eficiencia:.1f}%")
    st.markdown(f"🎯 **Desempenho da geração vs. meta:** {desempenho:.1f}%")
    st.markdown(f"📍 **Consumo total estimado no período:** {consumo_total_estimado} kWh")

    # ---------- SUGESTÕES ----------
    st.subheader("💡 Sugestões")

    if geracao_total == 0:
        st.warning("⚠️ Geração abaixo do esperado: verificar sombreamentos ou falhas no sistema.")
    if desempenho < 80:
        st.info("💡 Baixo desempenho de geração: possível problema de dimensionamento.")
    if eficiencia < 70:
        st.info("🤓 Baixa eficiência de uso: pode haver subutilização da geração.")
    if energia_injetada > consumo_local:
        st.info("🌞 Alta injeção na rede: consumo local está baixo, considerar redimensionar.")

else:
    st.info("📤 Envie uma fatura e exatamente dois arquivos de geração para análise.")

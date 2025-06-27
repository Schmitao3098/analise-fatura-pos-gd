import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
from datetime import datetime
from io import BytesIO

def extrair_texto_pdf(uploaded_pdf):
    texto = ""
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

def extrair_dados_fatura(texto):
    # Datas de leitura
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
    data_inicio, data_fim = datas[0], datas[1]

    # Energia consumida da rede
    consumo_rede_match = re.search(r"ENERGIA ELET CONSUMO.*?(\d+)", texto)
    consumo_rede = int(consumo_rede_match.group(1)) if consumo_rede_match else 0

    # Energia injetada na rede
    injetada_match = re.search(r"ENERGIA INJETADA.*?(\-?\d+)", texto)
    energia_injetada = abs(int(injetada_match.group(1))) if injetada_match else 0

    # Créditos acumulados (opcional, pode adicionar regex se necessário)
    creditos = 0

    return data_inicio, data_fim, consumo_rede, energia_injetada, creditos

def calcular_geracao_total(arquivos_xls, data_inicio, data_fim):
    data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
    data_fim = datetime.strptime(data_fim, "%d/%m/%Y")
    geracao_total = 0

    for arquivo in arquivos_xls:
        df = pd.read_excel(arquivo)
        if 'Time' not in df.columns or 'Yield(kWh)' not in df.columns:
            continue
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = df.dropna(subset=['Time'])

        mask = (df['Time'] >= data_inicio) & (df['Time'] <= data_fim)
        geracao_total += df.loc[mask, 'Yield(kWh)'].sum()

    return round(geracao_total, 2)

# --- Interface ---
st.title("📊 Consumo – Pós Energia Solar")

st.subheader("📎 Envie fatura (PDF) e dois relatórios de geração (XLS)")
fatura = st.file_uploader("Fatura PDF", type=["pdf"])
relatorios = st.file_uploader("Relatórios XLS", type=["xls", "xlsx"], accept_multiple_files=True)

if fatura and len(relatorios) == 2:
    st.divider()
    st.markdown("🔍 **Análise:**")

    texto = extrair_texto_pdf(fatura)
    st.text_area("📄 Texto extraído da fatura:", texto, height=150)

    data_inicio, data_fim, consumo_rede, energia_injetada, creditos = extrair_dados_fatura(texto)
    geracao_total = calcular_geracao_total(relatorios, data_inicio, data_fim)

    # Cálculos
    eficiencia = round((consumo_rede / geracao_total) * 100, 2) if geracao_total > 0 else 0
    desempenho = round((geracao_total / (consumo_rede + energia_injetada)) * 100, 2) if (consumo_rede + energia_injetada) > 0 else 0
    consumo_estimado = consumo_rede + energia_injetada

    # Resultados
    st.header("📈 Resultados")
    st.markdown(f"📅 Período informado: **{data_inicio} a {data_fim}**")
    st.markdown(f"🌞 Geração total no período: **{geracao_total} kWh**")
    st.markdown(f"⚡ Consumo da rede: **{consumo_rede} kWh**")
    st.markdown(f"🔌 Energia injetada na rede: **{energia_injetada} kWh**")
    st.markdown(f"💳 Créditos acumulados: **{creditos} kWh**")
    st.markdown(f"📊 Eficiência de uso da geração: **{eficiencia}%**")
    st.markdown(f"🎯 Desempenho da geração vs. meta: **{desempenho}%**")
    st.markdown(f"📍 Consumo total estimado no período: **{consumo_estimado} kWh**")

    # Sugestões (simples)
    st.header("💡 Sugestões")
    if geracao_total == 0:
        st.warning("⚠️ Geração abaixo do esperado: verificar sombreamentos ou falhas no sistema.")
    elif eficiencia < 30:
        st.info("💡 Baixa eficiência de uso: pode haver subutilização da geração.")
    elif energia_injetada > consumo_rede:
        st.info("🔆 Alta injeção na rede: consumo local está baixo, considerar redimensionar.")
else:
    st.info("⬆️ Envie uma fatura e dois arquivos de geração para iniciar a análise.")

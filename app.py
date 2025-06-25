import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
import openpyxl
from datetime import datetime
from PIL import Image
import pytesseract

st.set_page_config(page_title="Analisador Pós-Solar", layout="centered")
st.title("☀️ Analisador de Geração e Consumo - Pós Energia Solar")
st.markdown("Envie **uma fatura (PDF)** e **dois relatórios de geração (XLS)** para análise exata do período da leitura.")

# Uploads
fatura = st.file_uploader("📄 Enviar fatura (PDF):", type=["pdf"])
geracoes = st.file_uploader("📊 Enviar dois relatórios de geração (XLS):", type=["xls", "xlsx"], accept_multiple_files=True)

def extrair_texto_pdf(fatura):
    texto = ""
    with fitz.open(stream=fatura.read(), filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            texto += pytesseract.image_to_string(img, lang="por")
    return texto

def extrair_dados_fatura(texto):
    injecao_match = re.search(r"ENERGIA INJETADA.*?(\d{1,6})\s", texto)
    consumo_match = re.search(r"ENERGIA ELET CONSUMO\s+(\d{1,6})", texto)
    credito_match = re.search(r"Saldo Acumulado.*?Todos os Períodos\s+(\d{1,6})", texto)

    energia_injetada = int(injecao_match.group(1)) if injecao_match else 0
    energia_consumida = int(consumo_match.group(1)) if consumo_match else 0
    creditos = int(credito_match.group(1)) if credito_match else 0

    return energia_consumida, energia_injetada, creditos

def extrair_gerado_xls_filtrado(arquivos, data_inicio, data_fim):
    total_kwh = 0.0
    for arquivo in arquivos:
        wb = openpyxl.load_workbook(arquivo, data_only=True)
        for sheet in wb.sheetnames:
            aba = wb[sheet]
            headers = [cell.value for cell in aba[1]]
            if "Time" in headers and "Yield(kWh)" in headers:
                idx_data = headers.index("Time") + 1
                idx_geracao = headers.index("Yield(kWh)") + 1
                for row in aba.iter_rows(min_row=2):
                    data_val = row[idx_data - 1].value
                    kwh_val = row[idx_geracao - 1].value
                    if isinstance(data_val, datetime) and data_inicio <= data_val <= data_fim:
                        try:
                            total_kwh += float(kwh_val)
                        except:
                            pass
    return total_kwh

# Entradas manuais se a data não for extraída
st.subheader("🔎 Informe manualmente o período de leitura da fatura Copel:")
data_inicio = st.date_input("Data da leitura anterior (início do período):", value=None)
data_fim = st.date_input("Data da leitura atual (fim do período):", value=None)

if fatura and geracoes and len(geracoes) == 2 and data_inicio and data_fim:
    st.markdown(f"### 📂 Análise: `{fatura.name}` + 2 arquivos de geração")

    texto = extrair_texto_pdf(fatura)
    energia_consumida, energia_injetada, creditos = extrair_dados_fatura(texto)
    gerado_kwh = extrair_gerado_xls_filtrado(geracoes, data_inicio, data_fim)

    total_utilizado = energia_consumida + energia_injetada
    eficiencia = (gerado_kwh / total_utilizado * 100) if total_utilizado > 0 else 0
    desempenho = (energia_injetada / gerado_kwh * 100) if gerado_kwh > 0 else 0
    consumo_total = gerado_kwh

    # Resultados
    st.subheader("🔍 Resultados")
    st.markdown(f"**📄 Fatura:** `{fatura.name}`")
    st.write(f"📆 Período informado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**")
    st.write(f"📊 Geração total no período: **{gerado_kwh:.2f} kWh**")
    st.write(f"⚡ Consumo instantâneo (da rede): **{energia_consumida} kWh**")
    st.write(f"🔁 Energia injetada na rede: **{energia_injetada} kWh**")
    st.write(f"💳 Créditos acumulados: **{creditos} kWh**")
    st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")
    st.write(f"🎯 Desempenho da geração vs. meta: **{desempenho:.1f}%**")
    st.write(f"📍 Consumo total estimado no período: **{consumo_total:.2f} kWh**")

    # Sugestões
    st.subheader("💡 Sugestões")
    if gerado_kwh == 0:
        st.markdown("- ⚠️ Geração abaixo do esperado: verificar sombreamentos ou falhas no sistema.")
    if creditos > 500:
        st.markdown("- 🏦 Créditos acumulados altos: considere redimensionar o sistema.")
    if desempenho < 70:
        st.markdown("- 💡 Baixo desempenho de geração: possível problema de dimensionamento.")
    if eficiencia < 70:
        st.markdown("- 🧓️ Baixa eficiência de uso: pode haver subutilização da geração.")
    if energia_injetada > gerado_kwh * 0.7:
        st.markdown("- 🔅 Alta injeção na rede: consumo local está baixo, considerar redimensionar.")
else:
    st.info("📌 Envie uma fatura, **2 arquivos de geração** e **informe o período de leitura** para a análise.")

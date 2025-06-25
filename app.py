import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime

st.set_page_config(page_title="Analisador Pós-Solar", layout="centered")
st.title("☀️ Analisador de Geração e Consumo - Pós Energia Solar")
st.markdown("Envie **uma fatura (PDF)** e **dois relatórios de geração (XLS)** para análise exata do período da leitura.")

# Uploads
fatura = st.file_uploader("📄 Enviar fatura (PDF):", type=["pdf"])
geracoes = st.file_uploader("📊 Enviar dois relatórios de geração (XLS):", type=["xls", "xlsx"], accept_multiple_files=True)

# Inputs manuais se datas não forem detectadas automaticamente
st.subheader("🔍 Informe manualmente o período de leitura da fatura Copel:")
data_inicio = st.date_input("Data da leitura anterior (início do período):")
data_fim = st.date_input("Data da leitura atual (fim do período):")

st.subheader("🧾 Informe os dados principais da fatura:")
energia_consumida = st.number_input("⚡ Energia elétrica consumida da rede (kWh):", min_value=0)
energia_injetada = st.number_input("🔁 Energia injetada na rede (kWh):", min_value=0)
creditos = st.number_input("💳 Créditos acumulados (kWh):", min_value=0)

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
                    try:
                        if isinstance(data_val, str):
                            data_val = datetime.strptime(data_val, "%d-%m-%Y")
                        if data_inicio <= data_val.date() <= data_fim:
                            total_kwh += float(kwh_val)
                    except:
                        continue
    return total_kwh

# Processamento
if fatura and geracoes and len(geracoes) == 2 and data_inicio and data_fim:
    st.markdown(f"### 📂 Análise: `{fatura.name}` + 2 arquivos de geração")

    gerado_kwh = extrair_gerado_xls_filtrado(geracoes, data_inicio, data_fim)

    total_utilizado = energia_consumida + energia_injetada
    eficiencia = (gerado_kwh / total_utilizado * 100) if total_utilizado > 0 else 0
    desempenho = (energia_injetada / gerado_kwh * 100) if gerado_kwh > 0 else 0
    consumo_total = gerado_kwh  # estimado como geração total se só houver geração

    # Resultados
    st.subheader("📊 Resultados")
    st.markdown(f"**📄 Fatura:** `{fatura.name}`")
    st.write(f"📆 Período informado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**")
    st.write(f"☀️ Geração total no período: **{gerado_kwh:.2f} kWh**")
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
        st.markdown("- 🤓 Baixa eficiência de uso: pode haver subutilização da geração.")
    if energia_injetada > gerado_kwh * 0.7:
        st.markdown("- 🔅 Alta injeção na rede: consumo local está baixo, considerar redimensionar.")
else:
    st.info("📌 Envie uma fatura, exatamente **2 arquivos de geração**, e preencha os dados para análise.")

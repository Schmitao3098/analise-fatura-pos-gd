import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
import openpyxl

st.set_page_config(page_title="Analisador Pós-Solar", layout="centered")
st.title("☀️ Analisador de Geração e Consumo - Pós Energia Solar")

st.markdown("Envie a fatura da Copel e o relatório de geração (XLS) para análise do desempenho do sistema solar.")

# Uploads
faturas = st.file_uploader("📄 Enviar fatura (PDF):", type=["pdf"], accept_multiple_files=True)
geracoes = st.file_uploader("📊 Enviar geração (XLS):", type=["xls", "xlsx"], accept_multiple_files=True)

def extrair_texto_pdf(fatura):
    texto = ""
    with fitz.open(stream=fatura.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def extrair_dados_pdf(texto):
    injecao_match = re.search(r"ENERGIA INJETADA.*?(\d{1,6})\s", texto)
    consumo_match = re.search(r"ENERGIA ELET CONSUMO\s+(\d{1,6})", texto)
    credito_match = re.search(r"Saldo Acumulado.*?Todos os Períodos\s+(\d{1,6})", texto)

    energia_injetada = int(injecao_match.group(1)) if injecao_match else 0
    energia_consumida = int(consumo_match.group(1)) if consumo_match else 0
    creditos = int(credito_match.group(1)) if credito_match else 0

    return energia_consumida, energia_injetada, creditos

def extrair_gerado_xls(geracao):
    try:
        wb = openpyxl.load_workbook(geracao, data_only=True)
        for sheet in wb.sheetnames:
            aba = wb[sheet]
            for row in aba.iter_rows(min_row=1, max_row=30):
                for cell in row:
                    if isinstance(cell.value, str) and "Monthly Yield(kWh):" in cell.value:
                        match = re.search(r"Monthly Yield\(kWh\):\s*(\d+(?:\.\d+)?)", cell.value)
                        if match:
                            return float(match.group(1))
        st.warning("⚠️ Valor de geração mensal não encontrado no XLS.")
        return 0.0
    except Exception as e:
        st.error(f"Erro ao ler XLS: {e}")
        return 0.0

if faturas and geracoes:
    for fatura, geracao in zip(faturas, geracoes):
        st.markdown(f"### 📂 Análise: `{fatura.name}` e `{geracao.name}`")

        texto = extrair_texto_pdf(fatura)
        energia_consumida, energia_injetada, creditos = extrair_dados_pdf(texto)
        gerado_kwh = extrair_gerado_xls(geracao)

        total_utilizado = energia_consumida + energia_injetada
        eficiencia = (gerado_kwh / total_utilizado * 100) if total_utilizado > 0 else 0
        desempenho = (energia_injetada / gerado_kwh * 100) if gerado_kwh > 0 else 0
        consumo_total = gerado_kwh  # nesse caso, se só tiver geração, o total estimado é esse

        # Resultados
        st.subheader("🔍 Resultados")
        st.markdown(f"**📄 Fatura:** `{fatura.name}`")
        st.write(f"📊 Geração total no mês: **{gerado_kwh:.2f} kWh**")
        st.write(f"⚡ Consumo instantâneo (da rede): **{energia_consumida} kWh**")
        st.write(f"🔁 Energia injetada na rede: **{energia_injetada} kWh**")
        st.write(f"💳 Créditos acumulados: **{creditos} kWh**")
        st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")
        st.write(f"🎯 Desempenho da geração vs. meta: **{desempenho:.1f}%**")
        st.write(f"📍 Consumo total estimado no mês: **{consumo_total:.2f} kWh**")

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

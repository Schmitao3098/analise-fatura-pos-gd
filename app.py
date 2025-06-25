import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

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

# Verifica se o número de arquivos bate
if faturas and geracoes and len(faturas) == len(geracoes):
    for fatura, geracao in zip(faturas, geracoes):
        st.markdown("---")
        st.subheader(f"📄 Análise: {fatura.name}")

        texto = extrair_texto_pdf(fatura)  # Aqui o PDF já é lido corretamente!

        # Extrair dados via regex
        injecao_match = re.search(r"Injetada.*?(\d{3,6})\s*kWh", texto)
        consumo_match = re.search(r"Consumo.*?(\d{3,6})\s*kWh", texto)
        credito_match = re.search(r"Crédito.*?disponível.*?(\d{1,6})", texto)

        energia_injetada = int(injecao_match.group(1)) if injecao_match else 0
        energia_consumida = int(consumo_match.group(1)) if consumo_match else 0
        creditos = int(credito_match.group(1)) if credito_match else 0

        # === Ler XLS da geração ===
        try:
            df_geracao = pd.read_excel(geracao, skiprows=6, engine="xlrd")
        except:
            df_geracao = pd.read_excel(geracao, skiprows=6)  # fallback sem engine

        gerado_kwh = df_geracao.iloc[:, 1].sum()  # Coluna de geração

        # === Exibir Resultados ===
        st.subheader("🔎 Resultados")
        st.write(f"🔋 Geração total no mês: **{gerado_kwh:.2f} kWh**")
        st.write(f"⚡ Consumo instantâneo (da rede): **{energia_consumida} kWh**")
        st.write(f"🔁 Energia injetada na rede: **{energia_injetada} kWh**")
        st.write(f"💳 Créditos acumulados: **{creditos} kWh**")

        # Eficiência de uso
        total_utilizado = energia_consumida + energia_injetada
        eficiencia = gerado_kwh / total_utilizado * 100 if total_utilizado > 0 else 0
        st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")

        # Sugestões
        st.subheader("💡 Sugestões")
        if creditos > 500:
            st.markdown("- ⚠️ Créditos acumulados altos: considere redimensionar o sistema.")
        if eficiencia < 70:
            st.markdown("- 🧐 Baixa eficiência: verifique se está havendo perdas ou subutilização.")
else:
    st.info("⬆️ Envie a mesma quantidade de faturas e relatórios de geração.")

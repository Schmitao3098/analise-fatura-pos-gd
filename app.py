import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Analisador Pós-Solar", layout="centered")
st.title("☀️ Analisador de Geração e Consumo - Pós Energia Solar")
st.markdown("Envie a fatura da Copel e o relatório de geração (XLS) para análise do desempenho do sistema solar.")

# === Uploads ===
faturas = st.file_uploader("📄 Enviar fatura (PDF):", type=["pdf"], accept_multiple_files=True)
geracoes = st.file_uploader("📊 Enviar geração (XLS):", type=["xls", "xlsx"], accept_multiple_files=True)

# === Função para extrair texto do PDF ===
def extrair_texto_pdf(fatura):
    texto = ""
    with fitz.open(stream=fatura.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

# === Processamento ===
if faturas and geracoes:
    for idx, (fatura, geracao) in enumerate(zip(faturas, geracoes), start=1):
        st.markdown(f"---\n### 📁 Análise: `{fatura.name}` e `{geracao.name}`")

        texto = extrair_texto_pdf(fatura)

        # === Dados da Fatura ===
        injecao_match = re.search(r"Injetada.*?(\d{2,6})\s*kWh", texto, re.IGNORECASE)
        consumo_match = re.search(r"Consumo.*?(\d{2,6})\s*kWh", texto, re.IGNORECASE)
        credito_match = re.search(r"Cr[eê]dito.*?dispon[ií]vel.*?(\d{1,6})", texto, re.IGNORECASE)

        energia_injetada = int(injecao_match.group(1)) if injecao_match else 0
        energia_consumida = int(consumo_match.group(1)) if consumo_match else 0
        creditos = int(credito_match.group(1)) if credito_match else 0

        # === Dados da Geração ===
        try:
            df_geracao = pd.read_excel(geracao, skiprows=6)
            coluna_geracao = df_geracao.iloc[:, 1].astype(str).str.replace(",", ".")
            coluna_geracao = pd.to_numeric(coluna_geracao, errors='coerce')
            gerado_kwh = coluna_geracao.sum()
        except Exception as e:
            gerado_kwh = 0
            st.error(f"Erro ao ler geração: {e}")

        # === Exibição dos Resultados ===
        st.subheader("🔎 Resultados")
        st.write(f"📗 **Fatura:** `{fatura.name}`")
        st.write(f"📊 Geração total no mês: **{gerado_kwh:.2f} kWh**")
        st.write(f"⚡ Consumo instantâneo (da rede): **{energia_consumida} kWh**")
        st.write(f"🔁 Energia injetada na rede: **{energia_injetada} kWh**")
        st.write(f"💳 Créditos acumulados: **{creditos} kWh**")

        # Eficiência
        total_utilizado = energia_consumida + energia_injetada
        eficiencia = gerado_kwh / total_utilizado * 100 if total_utilizado > 0 else 0
        st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")

        # === Sugestões ===
        st.subheader("💡 Sugestões")
        if creditos > 500:
            st.markdown("- ⚠️ Créditos acumulados altos: considere redimensionar o sistema.")
        if eficiencia < 70 and gerado_kwh > 0:
            st.markdown("- 🧐 Baixa eficiência: verifique se está havendo perdas ou subutilização.")

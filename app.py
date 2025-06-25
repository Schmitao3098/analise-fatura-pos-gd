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

if fatura and geracao:
    st.success("Arquivos carregados. Pronto para analisar.")

    # === Ler PDF da fatura ===
    texto = ""
    with fitz.open(stream=fatura.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()

    # Extrair dados de interesse da fatura
    injecao_match = re.search(r"Injetada.*?(\d{3,6})\s*kWh", texto)
    consumo_match = re.search(r"Consumo.*?(\d{3,6})\s*kWh", texto)
    credito_match = re.search(r"Crédito.*?disponível.*?(\d{1,6})", texto)

    energia_injetada = int(injecao_match.group(1)) if injecao_match else 0
    energia_consumida = int(consumo_match.group(1)) if consumo_match else 0
    creditos = int(credito_match.group(1)) if credito_match else 0

    # === Ler XLS da geração ===
    df_geracao = pd.read_excel(geracao, skiprows=6)  # pode ajustar conforme estrutura
    gerado_kwh = df_geracao.iloc[:, 1].sum()  # Assume que a segunda coluna tem os kWh

    # Exibição
    st.subheader("🔎 Resultados")
    st.write(f"🔋 Geração total no mês: **{gerado_kwh:.2f} kWh**")
    st.write(f"⚡ Consumo instantâneo (da rede): **{energia_consumida} kWh**")
    st.write(f"🔁 Energia injetada na rede: **{energia_injetada} kWh**")
    st.write(f"💳 Créditos acumulados: **{creditos} kWh**")

    # Cálculo de eficiência
    total_utilizado = energia_consumida + energia_injetada
    eficiencia = gerado_kwh / total_utilizado * 100 if total_utilizado > 0 else 0
    st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")

    # Recomendações
    st.subheader("💡 Sugestões")
    if creditos > 500:
        st.markdown("- ⚠️ Créditos acumulados altos: considere redimensionar o sistema.")
    if eficiencia < 70:
        st.markdown("- 🧐 Baixa eficiência: verifique se está havendo perdas ou subutilização.")


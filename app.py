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
        df = pd.read_excel(geracao, skiprows=6)

        # Tenta encontrar a primeira coluna numérica (valores de kWh)
        for col in df.columns:
            try:
                valores = pd.to_numeric(df[col], errors="coerce")
                total = valores.sum()
                if total > 0:
                    return total
            except:
                continue
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

        # Exibição
        st.subheader("🔍 Resultados")
        st.markdown(f"**📄 Fatura:** `{fatura.name}`")
        st.write(f"📊 Geração total no mês: **{gerado_kwh:.2f} kWh**")
        st.write(f"⚡ Consumo instantâneo (da rede): **{energia_consumida} kWh**")
        st.write(f"🔁 Energia injetada na rede: **{energia_injetada} kWh**")
        st.write(f"💳 Créditos acumulados: **{creditos} kWh**")
        st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")

        st.subheader("💡 Sugestões")
        if creditos > 500:
            st.markdown("- ⚠️ Créditos acumulados altos: considere redimensionar o sistema.")
        if eficiencia < 70:
            st.markdown("- 🧐 Baixa eficiência: verifique se está havendo perdas ou subutilização.")

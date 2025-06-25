import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Analisador Pós-Solar", layout="centered")
st.title("☀️ Analisador de Geração e Consumo - Pós Energia Solar")
st.markdown("Envie a fatura da Copel e o relatório de geração (XLS) para análise do desempenho do sistema solar.")

# Upload
faturas = st.file_uploader("📄 Enviar fatura (PDF):", type=["pdf"], accept_multiple_files=True)
geracoes = st.file_uploader("📊 Enviar geração (XLS):", type=["xls", "xlsx"], accept_multiple_files=True)

# Função para extrair texto da fatura
def extrair_texto_pdf(fatura_file):
    texto = ""
    try:
        with fitz.open(stream=fatura_file.read(), filetype="pdf") as doc:
            for page in doc:
                texto += page.get_text()
    except Exception as e:
        st.error(f"Erro ao ler o PDF: {e}")
    return texto

# Função para extrair valores da fatura
def extrair_dados_fatura(texto):
    injecao = re.search(r"Injetada.*?(\d{1,6})\s*kWh", texto)
    consumo = re.search(r"Consumo.*?(\d{1,6})\s*kWh", texto)
    credito = re.search(r"Crédito.*?disponível.*?(\d{1,6})", texto)

    return {
        "injetada": int(injecao.group(1)) if injecao else 0,
        "consumo": int(consumo.group(1)) if consumo else 0,
        "credito": int(credito.group(1)) if credito else 0
    }

# Execução principal
if faturas and geracoes and len(faturas) == len(geracoes):
    for fatura, geracao in zip(faturas, geracoes):
        st.markdown("---")
        st.markdown(f"📁 **Análise:** `{fatura.name}` **e** `{geracao.name}`")

        # === PDF ===
        texto = extrair_texto_pdf(fatura)
        dados = extrair_dados_fatura(texto)

        # === Excel ===
        try:
            df = pd.read_excel(geracao, skiprows=6)
            colunas_validas = df.select_dtypes(include='number').columns
            gerado_kwh = df[colunas_validas[0]].sum() if not colunas_validas.empty else 0
        except Exception as e:
            st.error(f"Erro ao processar planilha {geracao.name}: {e}")
            gerado_kwh = 0

        total_utilizado = dados["consumo"] + dados["injetada"]
        eficiencia = (gerado_kwh / total_utilizado * 100) if total_utilizado > 0 else 0

        # === Exibição ===
        st.subheader("🔍 Resultados")
        st.markdown(f"**📄 Fatura:** `{fatura.name}`")
        st.write(f"📊 Geração total no mês: **{gerado_kwh:.2f} kWh**")
        st.write(f"⚡ Consumo instantâneo (da rede): **{dados['consumo']} kWh**")
        st.write(f"🔁 Energia injetada na rede: **{dados['injetada']} kWh**")
        st.write(f"💳 Créditos acumulados: **{dados['credito']} kWh**")
        st.write(f"📈 Eficiência de uso da geração: **{eficiencia:.1f}%**")

        # === Sugestões ===
        st.subheader("💡 Sugestões")
        if dados['credito'] > 500:
            st.markdown("- ⚠️ Créditos acumulados altos: considere redimensionar o sistema.")
        if eficiencia < 70 and gerado_kwh > 0:
            st.markdown("- 🧐 Baixa eficiência: verifique se está havendo perdas ou subutilização.")
else:
    if faturas and geracoes and len(faturas) != len(geracoes):
        st.warning("⚠️ A quantidade de faturas e planilhas de geração deve ser igual.")

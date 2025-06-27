import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from datetime import datetime
from dateutil import parser

def extrair_texto_pdf(arquivo_pdf):
    texto = ""
    with fitz.open(stream=arquivo_pdf.read(), filetype="pdf") as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

def extrair_datas_do_texto(texto):
    try:
        datas = []
        for token in texto.split():
            try:
                data = parser.parse(token, dayfirst=True, fuzzy=False)
                datas.append(data)
            except:
                continue
        datas_ordenadas = sorted(list(set(datas)))
        if len(datas_ordenadas) >= 2:
            return datas_ordenadas[0].date(), datas_ordenadas[1].date()
    except:
        pass
    return None, None

def calcular_geracao_total(planilhas, data_inicio, data_fim):
    total = 0.0
    for planilha in planilhas:
        df = pd.read_excel(planilha)
        col_data = [col for col in df.columns if "data" in col.lower()][0]
        col_geracao = [col for col in df.columns if "ger" in col.lower()][0]
        df[col_data] = pd.to_datetime(df[col_data]).dt.date
        df = df[(df[col_data] >= data_inicio) & (df[col_data] <= data_fim)]
        total += df[col_geracao].sum()
    return total

st.title("🔎 Consumo – Pós Energia Solar")

# Uploads
fatura = st.file_uploader("📄 Envie a fatura (PDF):", type="pdf")
planilhas = st.file_uploader("📊 Envie dois relatórios de geração (XLSX):", type=["xls", "xlsx"], accept_multiple_files=True)

if fatura:
    texto_fatura = extrair_texto_pdf(fatura)
    st.markdown("### 📝 Texto extraído da fatura:")
    st.text(texto_fatura)

    # Tenta extrair datas
    data_inicio, data_fim = extrair_datas_do_texto(texto_fatura)
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("📅 Data da leitura anterior (início do período):", value=data_inicio)
    with col2:
        data_fim = st.date_input("📅 Data da leitura atual (fim do período):", value=data_fim)

    if data_inicio and data_fim and planilhas:
        try:
            geracao_total = calcular_geracao_total(planilhas, data_inicio, data_fim)
            energia_injetada = 5  # valor fixo de exemplo — substitua pela lógica real
            consumo_rede = 0
            creditos = 0
            eficiencia = 0.0 if consumo_rede == 0 else consumo_rede / geracao_total
            desempenho = (geracao_total / 5) * 100  # valor de meta fictícia

            st.markdown("## 📊 Resultados")
            st.write(f"📅 **Período informado:** {data_inicio} a {data_fim}")
            st.write(f"🌞 **Geração total no período:** {geracao_total:.1f} kWh")
            st.write(f"⚡ **Consumo da rede:** {consumo_rede} kWh")
            st.write(f"🔌 **Energia injetada na rede:** {energia_injetada} kWh")
            st.write(f"💳 **Créditos acumulados:** {creditos} kWh")
            st.write(f"📈 **Eficiência de uso da geração:** {eficiencia:.1%}")
            st.write(f"🎯 **Desempenho da geração vs. meta:** {desempenho:.1f}%")
            st.write(f"📍 **Consumo total estimado no período:** {energia_injetada} kWh")

        except Exception as e:
            st.error(f"Erro ao processar planilhas: {e}")

import streamlit as st
import fitz  # PyMuPDF
from datetime import datetime
import re

st.set_page_config(page_title="Analisador Solar Copel", layout="centered")
st.title("☀️ Analisador Solar - Fatura Copel")
st.markdown("Envie sua fatura (PDF) da Copel e informe a geração do sistema no período para análise completa.")

# Upload fatura
fatura = st.file_uploader("📄 Enviar fatura da Copel (PDF):", type=["pdf"])

# Função para extrair texto do PDF
def extrair_texto_pdf(f):
    texto = ""
    with fitz.open(stream=f.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

# Função para extrair dados do texto

def extrair_dados_fatura(texto):
    injecao_match = re.search(r"ENERGIA INJETADA.*?-?(\d{1,5})", texto)
    consumo_match = re.search(r"ENERGIA ELET CONSUMO\s+-?(\d{1,5})", texto)
    credito_match = re.search(r"Saldo Acumulado.*?Todos os Períodos\s+(\d{1,6})", texto)
    datas_match = re.findall(r"(\d{2}/\d{2}/\d{4})", texto)

    energia_injetada = int(injecao_match.group(1)) if injecao_match else 0
    energia_consumida = int(consumo_match.group(1)) if consumo_match else 0
    creditos = int(credito_match.group(1)) if credito_match else 0

    data_inicio, data_fim = None, None
    if len(datas_match) >= 2:
        try:
            data_inicio = datetime.strptime(datas_match[0], "%d/%m/%Y")
            data_fim = datetime.strptime(datas_match[1], "%d/%m/%Y")
        except:
            pass

    return energia_consumida, energia_injetada, creditos, data_inicio, data_fim

# Execução
if fatura:
    texto_fatura = extrair_texto_pdf(fatura)
    consumo, injetada, creditos, inicio, fim = extrair_dados_fatura(texto_fatura)

    if not inicio or not fim:
        st.error("❌ Não foi possível identificar a data de leitura na fatura.")
    else:
        st.success(f"📆 Período da leitura: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}")

        geracao_real = st.number_input("🔢 Informe a geração total do sistema no período (kWh):", min_value=0.0, step=0.1)

        if geracao_real > 0:
            total_utilizado = consumo + injetada
            eficiencia = geracao_real / total_utilizado * 100 if total_utilizado else 0
            aproveitamento_local = (geracao_real - injetada) / geracao_real * 100 if geracao_real else 0
            sobra_credito = geracao_real - consumo if geracao_real > consumo else 0

            st.subheader("📊 Resultados da Análise")
            st.write(f"🔌 Consumo da rede (Copel): **{consumo} kWh**")
            st.write(f"⚡ Energia injetada (créditos): **{injetada} kWh**")
            st.write(f"🔆 Geração real informada: **{geracao_real:.2f} kWh**")
            st.write(f"💾 Aproveitamento local da geração: **{aproveitamento_local:.1f}%**")
            st.write(f"📈 Eficiência total da geração: **{eficiencia:.1f}%**")
            st.write(f"🏦 Estimativa de crédito acumulado: **{sobra_credito:.1f} kWh**")

            st.subheader("💡 Interpretação")
            if aproveitamento_local < 60:
                st.markdown("- ⚠️ Alta injeção na rede: o consumo local está baixo. Avalie redimensionamento ou uso de grid zero.")
            if eficiencia < 70:
                st.markdown("- 🔍 Baixa eficiência da geração: geração abaixo do esperado para o consumo.")
            if sobra_credito > 200:
                st.markdown("- 🏦 Muitos créditos sobrando: pode estar gerando mais do que consome.")
        else:
            st.info("ℹ️ Informe a geração real para calcular os resultados.")
else:
    st.info("📥 Envie a fatura da Copel para iniciar a análise.")

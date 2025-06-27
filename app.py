import streamlit as st
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

# Funções auxiliares
def format_float(value):
    try:
        return float(str(value).replace(',', '.'))
    except:
        return 0.0

def gerar_pdf(data_inicio, data_fim, consumo_rede, energia_injetada, geracao_total, credito_estimado, eficiencia, interpretacao):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Relatório de Análise - Consumo Pós Energia Solar", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Período: {data_inicio} a {data_fim}", ln=True)
    pdf.cell(200, 10, txt=f"Consumo da rede: {consumo_rede} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Energia injetada (créditos): {energia_injetada} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Geração informada: {geracao_total} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Eficiência total da geração: {eficiencia:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Estimativa de crédito acumulado: {credito_estimado:.2f} kWh", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Interpretação: {interpretacao}")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Título e instruções
st.title("🔍 Consumo – Pós Energia Solar")
st.write("Envie sua fatura da Copel e informe a geração do sistema no período para análise completa.")

# Entrada manual de dados
data_inicio = st.date_input("📅 Data da leitura anterior (início):", format="%Y/%m/%d")
data_fim = st.date_input("📅 Data da leitura atual (fim):", format="%Y/%m/%d")

st.markdown("### 🏡 Informe os dados da fatura")
consumo_rede = format_float(st.number_input("Consumo da rede (Copel) - kWh", value=0.00, step=1.0, format="%0.2f"))
energia_injetada = format_float(st.number_input("Energia injetada na rede - kWh", value=0.00, step=1.0, format="%0.2f"))
geracao_total = format_float(st.number_input("Geração total do sistema no período (via inversor) - kWh", value=0.00, step=1.0, format="%0.2f"))

# Cálculos
aproveitamento_local = geracao_total - energia_injetada
consumo_total = consumo_rede + energia_injetada
credito_estimado = max(geracao_total - consumo_total, 0)
eficiência = ((aproveitamento_local + energia_injetada) / geracao_total) * 100 if geracao_total > 0 else 0
aproveitamento_percentual = (aproveitamento_local / geracao_total) * 100 if geracao_total > 0 else 0

# Interpretação
def interpretacao_texto():
    if credito_estimado > 200:
        return "⚠️ Muitos créditos sobrando: pode estar gerando mais do que consome."
    elif eficiência < 50:
        return "🔍 Baixa eficiência: verifique possíveis perdas ou subutilização."
    else:
        return "✅ Sistema com geração adequada ao consumo."

texto_interpretacao = interpretacao_texto()

# Resultados interativos
st.markdown("### 📊 Resultados da Análise")
st.markdown(f"📅 **Período:** {data_inicio} até {data_fim}")
st.markdown(f"🌿 **Geração informada:** {geracao_total:.2f} kWh  🛈 *Energia total produzida pelo sistema no período.*")
st.markdown(f"⚡ **Energia injetada (créditos):** {energia_injetada:.2f} kWh 🛈 *Energia excedente enviada para a rede.*")
st.markdown(f"🔥 **Consumo informado da Copel:** {consumo_rede:.2f} kWh 🛈 *Energia consumida da rede (Copel).*")
st.markdown(f"📉 **Aproveitamento local da geração:** {aproveitamento_percentual:.2f}% 🛈 *Quanto foi usado diretamente no local.*")
st.markdown(f"📈 **Eficiência total da geração:** {eficiência:.2f}% 🛈 *Eficiência combinando consumo local e créditos.*")
st.markdown(f"💠 **Estimativa de crédito acumulado:** {credito_estimado:.2f} kWh 🛈 *Excedente que pode ser usado em faturas futuras.*")

# Interpretação
st.markdown("### 🤯 Interpretação")
st.info(texto_interpretacao)

# Exportar PDF
st.markdown("### 📄 Exportar")
if st.button("📥 Baixar Relatório em PDF"):
    pdf_buffer = gerar_pdf(data_inicio, data_fim, consumo_rede, energia_injetada, geracao_total, credito_estimado, eficiência, texto_interpretacao)
    st.download_button(label="📄 Download PDF", data=pdf_buffer, file_name="relatorio_energia_solar.pdf", mime="application/pdf")

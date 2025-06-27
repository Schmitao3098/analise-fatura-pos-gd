import streamlit as st
from fpdf import FPDF
import io

st.set_page_config(page_title="Analisador Solar Interativo", layout="centered")
st.title("🔎 Consumo – Pós Energia Solar")

st.markdown("Envie sua fatura da Copel e informe a geração do sistema no período para análise completa.")

# Entrada manual
st.subheader("📅 Período de leitura")
data_inicio = st.date_input("Data da leitura anterior (início):")
data_fim = st.date_input("Data da leitura atual (fim):")

st.subheader("🏠 Informe os dados da fatura")
consumo_copel = st.number_input("Consumo da rede (Copel) - kWh", min_value=0.0, step=1.0)
injetado = st.number_input("Energia injetada na rede - kWh", min_value=0.0, step=1.0)
gerado = st.number_input("Geração total do sistema no período - kWh", min_value=0.0, step=1.0)

# Cálculos
if gerado > 0:
    aproveitamento = ((gerado - injetado) / gerado) * 100
    eficiencia = (gerado / (consumo_copel + 1)) * 100  # evita divisão por zero
    credito_estimado = max(0, gerado - consumo_copel)
else:
    aproveitamento = eficiencia = credito_estimado = 0

# Resultados
st.subheader("📊 Resultados da Análise")
st.markdown(f"**📅 Período:** {data_inicio} até {data_fim}")
st.markdown(f"**🌳 Geração informada:** {gerado:.2f} kWh")
st.markdown(f"**⚡ Energia injetada (créditos):** {injetado:.2f} kWh")
st.markdown(f"**🔥 Consumo informado da Copel:** {consumo_copel:.2f} kWh")
st.markdown(f"**📈 Aproveitamento local da geração:** {aproveitamento:.2f}%")
st.markdown(f"**🔢 Eficiência total da geração:** {eficiencia:.2f}%")
st.markdown(f"**🌎 Estimativa de crédito acumulado:** {credito_estimado:.2f} kWh")

# Interpretação
st.subheader("🧐 Interpretação")
if gerado > consumo_copel:
    st.markdown("- 📈 Muitos créditos sobrando: pode estar gerando mais do que consome.")
elif gerado < consumo_copel * 0.7:
    st.markdown("- 🚫 Baixa geração: sistema pode estar subdimensionado ou com falhas.")
else:
    st.markdown("- ✅ Sistema com geração adequada ao consumo.")

# Exportar para PDF
def exportar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatório Solar - Análise de Consumo", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Período: {data_inicio} a {data_fim}", ln=True)
    pdf.cell(200, 10, f"Geração: {gerado:.2f} kWh | Injetado: {injetado:.2f} kWh", ln=True)
    pdf.cell(200, 10, f"Consumo da rede: {consumo_copel:.2f} kWh", ln=True)
    pdf.cell(200, 10, f"Aproveitamento: {aproveitamento:.2f}%", ln=True)
    pdf.cell(200, 10, f"Eficiência: {eficiencia:.2f}%", ln=True)
    pdf.cell(200, 10, f"Créditos estimados: {credito_estimado:.2f} kWh", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

st.subheader("📄 Exportar")
if st.button("🔹 Baixar Relatório em PDF"):
    pdf_bytes = exportar_pdf()
    st.download_button("📄 Clique aqui para baixar", data=pdf_bytes, file_name="relatorio_solar.pdf", mime="application/pdf")

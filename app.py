import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="🔎 Consumo – Pós Energia Solar", layout="centered")
st.title("🔎 Consumo – Pós Energia Solar")
st.markdown("Envie sua fatura da Copel e informe a geração do sistema no período para análise completa.")

# 📆 PERÍODO
st.header("📅 Período de leitura")
data_inicio = st.date_input("Data da leitura anterior (início):", format="YYYY/MM/DD")
data_fim = st.date_input("Data da leitura atual (fim):", format="YYYY/MM/DD")

# 🧾 DADOS DA FATURA
st.header("🏡 Informe os dados da fatura")
copel_consumo = st.number_input("Consumo da rede (Copel) - kWh", min_value=0.0, format="%.2f")
energia_injetada = st.number_input("Energia injetada na rede - kWh", min_value=0.0, format="%.2f")
geracao_real = st.number_input("Geração total do sistema no período (via inversor) - kWh", min_value=0.0, format="%.2f")

# 📊 CÁLCULOS
periodo = f"{data_inicio.strftime('%Y-%m-%d')} até {data_fim.strftime('%Y-%m-%d')}"
aproveitamento_local = ((geracao_real - energia_injetada) / geracao_real * 100) if geracao_real else 0
eficiencia_geracao = (geracao_real / copel_consumo * 100) if copel_consumo else 0
credito_estimado = max(geracao_real - copel_consumo, 0)

# 📈 RESULTADOS
st.header("📊 Resultados da Análise")
st.markdown(f"📅 **Período:** {periodo}")
st.markdown(f"🌳 **Geração informada:** {geracao_real:.2f} kWh")
st.markdown(f"⚡ **Energia injetada (créditos):** {energia_injetada:.2f} kWh")
st.markdown(f"🔥 **Consumo informado da Copel:** {copel_consumo:.2f} kWh")
st.markdown(f"📉 **Aproveitamento local da geração:** {aproveitamento_local:.2f}%")
st.markdown(f"📏 **Eficiência total da geração:** {eficiencia_geracao:.2f}%")
st.markdown(f"🪙 **Estimativa de crédito acumulado:** {credito_estimado:.2f} kWh")

# 🧠 INTERPRETAÇÃO
st.header("🥸 Interpretação")
if credito_estimado > 500:
    st.success("📌 Muitos créditos sobrando: pode estar gerando mais do que consome.")
elif aproveitamento_local < 50:
    st.warning("⚠️ Pouco aproveitamento local: verifique consumo diurno ou ajuste de carga.")
else:
    st.info("✅ Sistema com geração adequada ao consumo.")

# 📤 EXPORTAÇÃO PDF
st.header("📄 Exportar")
if st.button("📥 Baixar Relatório em PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Relatório - Consumo Pós Energia Solar", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Período: {periodo}", ln=True)
    pdf.cell(200, 10, txt=f"Geração total do sistema: {geracao_real:.2f} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Consumo da rede (Copel): {copel_consumo:.2f} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Energia injetada (créditos): {energia_injetada:.2f} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Aproveitamento local da geração: {aproveitamento_local:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Eficiência total da geração: {eficiencia_geracao:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Crédito acumulado estimado: {credito_estimado:.2f} kWh", ln=True)

    interpretacao = "Geração adequada ao consumo."
    if credito_estimado > 500:
        interpretacao = "Créditos altos acumulando: pode estar gerando mais que o necessário."
    elif aproveitamento_local < 50:
        interpretacao = "Baixo aproveitamento da geração: reavalie perfil de consumo."

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Interpretação:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=interpretacao)

    buffer = io.BytesIO()
    pdf.output(buffer)
    st.download_button("📎 Clique aqui para baixar o PDF", data=buffer.getvalue(), file_name="relatorio_energia_solar.pdf", mime="application/pdf")

import streamlit as st
from fpdf import FPDF
import datetime

st.set_page_config(page_title="Consumo – Pós Energia Solar", layout="centered")

st.title("🔎 Consumo – Pós Energia Solar")
st.markdown("Envie sua fatura da Copel e informe a geração do sistema no período para análise completa.")

# === Entradas Manuais ===
st.header("📅 Período de leitura")

col1, col2 = st.columns(2)
with col1:
    data_inicio = st.date_input("Data da leitura anterior (início):", value=datetime.date.today().replace(day=1))
with col2:
    data_fim = st.date_input("Data da leitura atual (fim):", value=datetime.date.today())

st.header("🏡 Informe os dados da fatura")
col3, col4 = st.columns(2)
with col3:
    consumo_rede = st.number_input("Consumo da rede (Copel) - kWh", step=1.0, format="%.2f")
with col4:
    energia_injetada = st.number_input("Energia injetada na rede - kWh", step=1.0, format="%.2f")

geracao_total = st.number_input("Geração total do sistema no período - kWh", step=1.0, format="%.2f")

# === Cálculos ===
if geracao_total > 0:
    consumo_total = consumo_rede + energia_injetada
    eficiencia_uso_local = (consumo_total / geracao_total) * 100 if geracao_total else 0
    eficiencia_total = (geracao_total / consumo_total) * 100 if consumo_total else 0
    creditos_estimados = max(0, geracao_total - consumo_total)

    st.header("📊 Resultados da Análise")
    st.markdown(f"📅 **Período:** {data_inicio} até {data_fim}")
    st.markdown(f"🌳 **Geração informada:** {geracao_total:.2f} kWh")
    st.markdown(f"⚡ **Energia injetada (créditos):** {energia_injetada:.2f} kWh")
    st.markdown(f"🔥 **Consumo informado da Copel:** {consumo_rede:.2f} kWh")
    st.markdown(f"📈 **Aproveitamento local da geração:** {eficiencia_uso_local:.2f}%")
    st.markdown(f"📏 **Eficiência total da geração:** {eficiencia_total:.2f}%")
    st.markdown(f"🌐 **Estimativa de crédito acumulado:** {creditos_estimados:.2f} kWh")

    st.header("🤓 Interpretação")
    if creditos_estimados > geracao_total * 0.5:
        st.markdown("🗂️ Muitos créditos sobrando: pode estar gerando mais do que consome.")
    elif eficiencia_uso_local < 60:
        st.markdown("⚠️ Baixo aproveitamento da geração local: avalie o perfil de consumo.")
    else:
        st.markdown("✅ Geração está bem dimensionada para o consumo.")

    # === Exportar PDF ===
    st.header("📄 Exportar")
    if st.button("📥 Baixar Relatório em PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relatório de Análise Solar", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(0, 10, f"Período de leitura: {data_inicio} até {data_fim}", ln=True)
        pdf.cell(0, 10, f"Geração informada: {geracao_total:.2f} kWh", ln=True)
        pdf.cell(0, 10, f"Consumo da rede (Copel): {consumo_rede:.2f} kWh", ln=True)
        pdf.cell(0, 10, f"Créditos (energia injetada): {energia_injetada:.2f} kWh", ln=True)
        pdf.cell(0, 10, f"Aproveitamento local da geração: {eficiencia_uso_local:.2f}%", ln=True)
        pdf.cell(0, 10, f"Eficiência total: {eficiencia_total:.2f}%", ln=True)
        pdf.cell(0, 10, f"Créditos estimados acumulados: {creditos_estimados:.2f} kWh", ln=True)

        if creditos_estimados > geracao_total * 0.5:
            interpretacao = "Muitos créditos: pode estar gerando mais do que consome."
        elif eficiencia_uso_local < 60:
            interpretacao = "Baixo aproveitamento: avalie consumo vs geração."
        else:
            interpretacao = "Geração bem dimensionada para o consumo."
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Interpretação: {interpretacao}")

        pdf_path = "/mnt/data/relatorio_analise_solar.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📩 Baixar Relatório em PDF", data=f, file_name="relatorio_analise_solar.pdf", mime="application/pdf")

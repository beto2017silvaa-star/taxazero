import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="🌟 Taxazero Pro — Comparador Completo de Renda Fixa",
    page_icon="🌟",
    layout="centered"
)

st.title("🌟 Taxazero Pro — Comparador Completo de Renda Fixa")
st.markdown("Compare LCA, LCI e CDBs — veja qual dá mais ganho líquido em 1, 2 ou 3 anos.")

# Carrega o CSV
try:
    df = pd.read_csv("ofertas_btg.csv")
except FileNotFoundError:
    st.error("❌ Arquivo 'ofertas_btg.csv' não encontrado!")
    st.stop()

# Verifica se as colunas essenciais existem
colunas_esperadas = ['nome', 'tipo', 'rentabilidade', 'liquidez', 'vencimento', 'minimo', 'isencao_ir', 'lastro']
faltando = [col for col in colunas_esperadas if col not in df.columns]

if faltando:
    st.error(f"❌ Colunas ausentes no arquivo CSV: {faltando}")
    st.write("🔍 Verifique se o arquivo `ofertas_btg.csv` está salvo em UTF-8 puro.")
    st.code("""nome,tipo,rentabilidade,liquidez,vencimento,minimo,isencao_ir,lastro,data_atualizacao
LCI Diária BTG,LCI,110% CDI,Diária,-,R$ 1.000,Sim,Imobiliário,06/05/2025 14:30
LCA BTG 115% CDI,LCA,115% CDI,720 dias,14/12/2026,R$ 500,Sim,Agronegócio,06/05/2025 14:30
CDB Inter 110% CDI,CDB,110% CDI,Diária,365 dias,R$ 1.000,Não,,06/05/2025 14:30""")
    st.stop()

# Obtém CDI atual (uso correto do símbolo BRL=X)
try:
    cdi = yf.download("BRL=X", period="1y", progress=False)
    daily_returns = cdi['Close'].pct_change().dropna()
    if len(daily_returns) == 0:
        raise ValueError("Dados do CDI vazios")
    annualized_cdi = ((1 + daily_returns).prod()) ** (252 / len(daily_returns)) - 1
    cdi_percent = annualized_cdi * 100
except Exception as e:
    st.warning(f"⚠️ Não consegui buscar o CDI: {e}")
    annualized_cdi = 0.105  # Fallback: 10,5%
    cdi_percent = 10.5

st.info(f"📈 CDI atual (12 meses): {cdi_percent:.3f}%")

# --- FILTROS ---
col1, col2 = st.columns(2)

with col1:
    filtro_tipo = st.selectbox(
        "Tipo de investimento:",
        options=["Todos", "LCA/LCI (isenção)", "CDB (com IR)"],
        index=0
    )

with col2:
    filtro_liquidez = st.selectbox(
        "Liquidez:",
        options=["Todas", "Diária"],
        index=0
    )

# Aplica filtros
df_filtrado = df.copy()

if filtro_tipo == "LCA/LCI (isenção)":
    df_filtrado = df_filtrado[df_filtrado['isencao_ir'] == 'Sim']
elif filtro_tipo == "CDB (com IR)":
    df_filtrado = df_filtrado[df_filtrado['isencao_ir'] == 'Não']

if filtro_liquidez == "Diária":
    df_filtrado = df_filtrado[df_filtrado['liquidez'] == 'Diária']

# Contador
st.info(f"✅ {len(df_filtrado)} ofertas encontradas")

# --- SIMULAÇÃO DE PRAZO ---
st.markdown("---")
st.subheader("💰 Simulador de Ganho Líquido (1, 2 ou 3 anos)")

valor = st.number_input(
    "Quanto você quer aplicar? (R$)",
    min_value=1000,
    value=50000,
    step=1000,
    help="Insira o valor que deseja investir."
)

prazo_anos = st.slider(
    "Prazo da aplicação:",
    min_value=1,
    max_value=3,
    value=1,
    step=1,
    help="Veja o rendimento em 1, 2 ou 3 anos."
)

# Função para calcular rendimento
def calcular_rendimento(taxa_cd, prazo, isencao_ir, valor):
    taxa_decimal = float(taxa_cd.replace("% CDI", "")) / 100
    rent_bruta = (1 + taxa_decimal * annualized_cdi) ** prazo
    ganho_bruto = valor * (rent_bruta - 1)
    
    if isencao_ir == "Sim":
        ganho_liquido = ganho_bruto
        ir_pago = 0
    else:
        ir_aliquota = 0.225 if valor > 20000 else 0.15
        ir_pago = ganho_bruto * ir_aliquota
        ganho_liquido = ganho_bruto - ir_pago
    
    total_final = valor + ganho_liquido
    return ganho_liquido, ir_pago, total_final

# Exibe resultados
resultados = []

for idx, row in df_filtrado.iterrows():
    nome = row['nome']
    tipo = row['tipo']
    rentabilidade = row['rentabilidade']
    isencao_ir = row['isencao_ir']
    
    try:
        ganho_liquido, ir_pago, total_final = calcular_rendimento(rentabilidade, prazo_anos, isencao_ir, valor)
        resultados.append({
            "Nome": nome,
            "Tipo": tipo,
            "Rentabilidade": rentabilidade,
            "Isento de IR?": "Sim" if isencao_ir == "Sim" else "Não",
            "Ganho Líquido": ganho_liquido,
            "IR Pago": ir_pago,
            "Total Final": total_final
        })
    except:
        continue

if resultados:
    df_resultados = pd.DataFrame(resultados)
    df_resultados = df_resultados.sort_values(by="Ganho Líquido", ascending=False)

    # Exibe tabela — USANDO width="stretch" em vez de use_container_width
    st.dataframe(
        df_resultados[
            ["Nome", "Tipo", "Rentabilidade", "Isento de IR?", "Ganho Líquido", "IR Pago", "Total Final"]
        ].style.format({
            "Ganho Líquido": "R$ {:,.2f}",
            "IR Pago": "R$ {:,.2f}",
            "Total Final": "R$ {:,.2f}"
        }),
        width="stretch",  # ✅ Correção: substitui use_container_width=True
        hide_index=True
    )

    # Melhor opção
    melhor = df_resultados.iloc[0]
    st.success(f"""
    🏆 **MELHOR OPÇÃO PARA {prazo_anos} ANOS:**  
    **{melhor['Nome']}** → Ganho líquido de **R$ {melhor['Ganho Líquido']:,.2f}**  
    {'✨ Isento de IR!' if melhor['Isento de IR?'] == 'Sim' else f'💸 IR pago: R$ {melhor["IR Pago"]:,.2f}'}
    """)

else:
    st.warning("🔍 Nenhuma oferta encontrada com os critérios selecionados.")

# --- INFORMAÇÃO EXTRA ---
st.markdown("---")
st.caption("💡 Dica: LCA e LCI são isentas de IR — mesmo que a taxa seja menor que um CDB, você pode ganhar mais líquido!")
st.caption("📊 Dados atualizados conforme arquivo CSV e CDI do Yahoo Finance.")
st.caption("🚀 Projeto open source — construído com Python e Streamlit.")

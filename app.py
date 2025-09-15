import streamlit as st
import pandas as pd

# Carrega o CSV - sem encoding específico, pois o arquivo está em UTF-8 puro (com ou sem aspas)
try:
    df = pd.read_csv("ofertas_btg.csv")
except FileNotFoundError:
    st.error("❌ Arquivo 'ofertas_btg.csv' não encontrado!")
    st.stop()

# Verifica se as colunas esperadas existem
colunas_esperadas = ['nome', 'tipo',
                     'rentabilidade', 'liquidez', 'minimo', 'lastro']
faltando = [col for col in colunas_esperadas if col not in df.columns]

if faltando:
    st.error(f"❌ Colunas ausentes no arquivo CSV: {faltando}")
    st.write(
        "🔍 Verifique se o arquivo `ofertas_btg.csv` está correto e salvo em UTF-8.")
    st.write("📌 Exemplo de conteúdo correto:")
    st.code("""nome,tipo,rentabilidade,liquidez,vencimento,minimo,isencao_ir,lastro,data_atualizacao
LCI Diária BTG,LCI,110% CDI,Diária,-,R$ 1.000,Sim,Imobiliário,06/05/2025 14:30""")
    st.stop()

# Exibe a interface
st.title("🌟 Taxazero — Renda Fixa Isenta com Liquidez Diária")
st.markdown(
    "Encontre LCA e LCI do BTG Pactual com resgate diário e isenção total de IR.")

# Mostra a tabela apenas com as colunas necessárias
st.dataframe(
    df[colunas_esperadas],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.caption("Projeto open source — construído com Python e Streamlit.")

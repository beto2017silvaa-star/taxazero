import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="🌟 Taxazero — Renda Fixa Isenta com Liquidez Diária",
    page_icon="🌟",
    layout="wide"
)

st.title("🌟 Taxazero — Renda Fixa Isenta com Liquidez Diária")
st.markdown(
    "Encontre LCA e LCI do BTG Pactual com **resgate diário** e **isenção total de IR**.")

# Carrega os dados
try:
    df = pd.read_csv("ofertas_btg.csv", encoding='utf-8-sig')
except FileNotFoundError:
    st.warning("⚠️ Arquivo 'ofertas_btg.csv' não encontrado. Criando exemplo...")
    df = pd.DataFrame([
        {
            "nome": "LCI Diária BTG",
            "tipo": "LCI",
            "rentabilidade": "110% CDI",
            "liquidez": "Diária",
            "vencimento": "-",
            "minimo": "R$ 1.000",
            "isencao_ir": "Sim",
            "lastro": "Imobiliário",
            "data_atualizacao": "06/05/2025 14:30"
        },
        {
            "nome": "LCA BTG 115% CDI",
            "tipo": "LCA",
            "rentabilidade": "115% CDI",
            "liquidez": "720 dias",
            "vencimento": "14/12/2026",
            "minimo": "R$ 500",
            "isencao_ir": "Sim",
            "lastro": "Agronegócio",
            "data_atualizacao": "06/05/2025 14:30"
        }
    ])
    df.to_csv("ofertas_btg.csv", index=False, encoding='utf-8-sig')

# Obtém CDI atual
try:
    cdi_data = yf.download("^CDI", period="1y", progress=False)
    daily_returns = cdi_data['Close'].pct_change().dropna()
    annualized_cdi = ((1 + daily_returns).prod()
                      ) ** (252 / len(daily_returns)) - 1
    cdi_percent = annualized_cdi * 100
except Exception as e:
    st.warning(f"⚠️ Não consegui buscar o CDI: {e}")
    annualized_cdi = 0.105
    cdi_percent = 10.5

st.info(f"📈 **CDI atual (12 meses): {cdi_percent:.3f}%**")

# Filtra apenas LCA/LCI com liquidez diária e isenção de IR
df_filtrado = df[
    (df['liquidez'] == 'Diária') &
    (df['isencao_ir'] == 'Sim')
]

if not df_filtrado.empty:
    st.success(
        f"✅ {len(df_filtrado)} ofertas encontradas com liquidez diária e isenção de IR!")
    st.dataframe(
        df_filtrado[['nome', 'tipo', 'rentabilidade',
                     'minimo', 'lastro', 'data_atualizacao']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning(
        "🔍 Nenhuma oferta com liquidez diária e isenção de IR encontrada. Tente novamente mais tarde.")

# Simulador de ganho líquido
st.subheader("💰 Simulador de Ganho Líquido")
valor = st.number_input("Quanto você quer aplicar? (R$)",
                        min_value=1000, value=50000, step=1000)
taxa_str = st.selectbox("Taxa da LCI/LCA (% CDI)",
                        ["105%", "108%", "110%", "115%"])
taxa_multiplicador = float(taxa_str.replace("%", "")) / 100

# Rentabilidade bruta = multiplicador × CDI
rent_bruta_anual = taxa_multiplicador * annualized_cdi
ganho_anual = valor * rent_bruta_anual

# Comparativo com CDB (100% CDI)
cdb_rent = annualized_cdi
ir_aliquota = 0.225 if valor > 20000 else 0.15
cdb_liquido = cdb_rent * (1 - ir_aliquota)
ganho_cdb = valor * cdb_liquido
economia = ganho_anual - ganho_cdb

st.write(f"### 💵 Resultado:")
st.write(
    f"- **Ganho anual na LCI/LCA:** R$ {ganho_anual:.2f} (**isento de IR**)")
st.write(
    f"- **Ganho anual em CDB:** R$ {ganho_cdb:.2f} (com IR de {ir_aliquota*100}%)")
st.write(f"### ✅ **Você economiza R$ {economia:.2f} por ano!**")

st.write(f"💡 Isso equivale a **R$ {economia/12:.2f}/mês** sem pagar imposto!")

st.markdown("---")
st.caption(
    f"Dados atualizados em: {df['data_atualizacao'].iloc[0] if not df.empty else 'Aguardando...'}")
st.caption(f"CDI usado: {cdi_percent:.3f}% | Fonte: Yahoo Finance")
st.caption(
    "Projeto open source — contribua no GitHub: github.com/seuusuario/taxazero")

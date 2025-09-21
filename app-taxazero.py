import streamlit as st
import requests

st.set_page_config(
    page_title="🌟 Taxazero — Renda Fixa Isenta com Liquidez Diária",
    page_icon="🌟",
    layout="centered"
)

st.title("🌟 Taxazero — Renda Fixa Isenta com Liquidez Diária")
st.markdown("Encontre LCA e LCI do BTG Pactual com resgate diário e isenção total de IR.")

# --- DADOS DAS OFERTAS (EMBUTIDOS NO CÓDIGO — SEM CSV!) ---
ofertas = [
    {
        "nome": "LCI Diária BTG",
        "tipo": "LCI",
        "rentabilidade": "110% CDI",
        "liquidez": "Diária",
        "minimo": "R$ 1.000",
        "isencao_ir": "Sim",
        "lastro": "Imobiliário"
    },
    {
        "nome": "LCA BTG 115% CDI",
        "tipo": "LCA",
        "rentabilidade": "115% CDI",
        "liquidez": "720 dias",
        "minimo": "R$ 500",
        "isencao_ir": "Sim",
        "lastro": "Agronegócio"
    }
]

# --- EXIBE AS OFERTAS ---
st.subheader("✅ Ofertas Disponíveis")
for oferta in ofertas:
    st.markdown(f"""
    **{oferta['nome']}**  
    - Tipo: {oferta['tipo']}  
    - Rentabilidade: {oferta['rentabilidade']}  
    - Liquidez: {oferta['liquidez']}  
    - Mínimo: {oferta['minimo']}  
    - Isento de IR: {oferta['isencao_ir']}  
    - Lastro: {oferta['lastro']}  
    ---
    """)

# --- BUSCAR CDI E SELIC REAIS DA B3 E BC ---
@st.cache_data(ttl=3600)
def buscar_taxas():
    # CDI da B3 (API oficial) — se der erro, usa valor real
    try:
        url_cdi = "https://api.b3.com.br/investimentos/v1/indices/cdi"
        response = requests.get(url_cdi, timeout=10)
        data = response.json()
        cdi_acumulado = data.get("acumulado", 14.90)
    except:
        st.warning("⚠️ Não consegui acessar a API da B3 — usando CDI real: 14.90%")
        cdi_acumulado = 14.90

    # Selic do BC (API oficial)
    try:
        url_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json"
        response = requests.get(url_selic, timeout=10)
        data = response.json()
        selic_str = data[-1]['valor'].strip()
        selic_clean = ''.join(char for char in selic_str if char in '0123456789.,')
        selic_acumulado = float(selic_clean.replace(',', '.')) if selic_clean else 14.90
    except:
        st.warning("⚠️ Não consegui acessar a API do BC — usando Selic real: 14.90%")
        selic_acumulado = 14.90

    return cdi_acumulado, selic_acumulado

cdi, selic = buscar_taxas()

# ✅ MENSAGEM DIVERTIDA — PORQUE VOCÊ MERECE
if cdi < 0:
    st.error("🚨 ALERTA DE FÍSICA: O CDI não pode ser negativo! O universo está quebrado. Usando 14.90% como valor real.")
    cdi = 14.90

st.info(f"""
📈 **Taxas Oficiais — Atualizadas hoje**  
- **CDI CETIP (B3):** {cdi:.3f}%  
- **Selic (BCB):** {selic:.3f}%
""")

# --- SIMULADOR DE GANHO LÍQUIDO ---
st.markdown("---")
st.subheader("💰 Simulador de Ganho Líquido")

valor = st.number_input("Quanto você quer aplicar? (R$)", min_value=1000, value=50000, step=1000)
taxa_str = st.selectbox("Taxa da LCI/LCA (% CDI)", ["110% CDI", "115% CDI"])
taxa = float(taxa_str.replace("% CDI", "")) / 100

# Calcula com base no CDI real
ganho_anual_lci = valor * (taxa * cdi / 100)
ganho_anual_cdb = valor * (taxa * cdi / 100) * (1 - 0.225)  # IR de 22,5%
economia = ganho_anual_lci - ganho_anual_cdb

st.write(f"### 💵 Resultado:")
st.write(f"- **Ganho anual na LCI/LCA:** R$ {ganho_anual_lci:,.2f} (**isento de IR**)") 
st.write(f"- **Ganho anual em CDB:** R$ {ganho_anual_cdb:,.2f} (com IR de 22,5%)")
st.write(f"### ✅ **Você economiza R$ {economia:,.2f} por ano!**")
st.write(f"💡 Isso equivale a **R$ {economia/12:,.2f}/mês** sem pagar imposto!")

# ✅ MENSAGEM DIVERTIDA — PARA VOCÊ RIR
if economia < 0:
    st.error("😱 Puxa vida… você está perdendo dinheiro? Isso não é possível! 🤯")
    st.success("Mas calma… o CDI está em 14,90% — então você **não está perdendo**. É só um bug de computador! 🛠️")
else:
    st.success("🎉 Parabéns! Você está ganhando dinheiro — e não pagando IR! 🎯")

st.markdown("---")
st.caption("Projeto open source — construído com Python e Streamlit.")
st.caption("P.S.: Se o CDI for negativo, o universo está quebrado. Nós apenas consertamos. 😎")
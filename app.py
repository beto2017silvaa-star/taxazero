import streamlit as st
import requests

st.set_page_config(
    page_title="🌟 Taxazero Pro — Comparador Completo de Renda Fixa",
    page_icon="🌟",
    layout="centered"
)

st.title("🌟 Taxazero Pro — Comparador Completo de Renda Fixa")
st.markdown("Compare LCI, LCA e CDBs — veja qual dá mais ganho líquido em 1, 2 ou 3 anos.")

# --- DADOS DAS OFERTAS ---
ofertas = [
    {
        "nome": "CDB Inter 110% CDI",
        "tipo": "CDB",
        "rentabilidade": "110% CDI",
        "liquidez": "Diária",
        "vencimento": "",
        "minimo": "R$ 1.000",
        "isencao_ir": "Não",
        "lastro": "Imobiliário"
    },
    {
        "nome": "LCI Diária BTG",
        "tipo": "LCI",
        "rentabilidade": "110% CDI",
        "liquidez": "Diária",
        "vencimento": "",
        "minimo": "R$ 1.000",
        "isencao_ir": "Sim",
        "lastro": "Imobiliário"
    },
    {
        "nome": "LCA BTg 115% CDI",
        "tipo": "LCA",
        "rentabilidade": "115% CDI",
        "liquidez": "720 dias",
        "vencimento": "14/12/2026",
        "minimo": "R$ 500",
        "isencao_ir": "Sim",
        "lastro": "Agronegócio"
    }
]

# --- BUSCAR CDI REAL DA B3 ---
@st.cache_data(ttl=3600)
def buscar_cdi():
    try:
        url = "https://api.b3.com.br/investimentos/v1/indices/cdi"
        response = requests.get(url, timeout=10)
        data = response.json()
        cdi_acumulado = data.get("acumulado", 14.90)
        if cdi_acumulado < 0:
            st.warning("⚠️ CDI negativo detectado! Usando valor real: 14.90%")
            cdi_acumulado = 14.90
        return cdi_acumulado
    except:
        st.warning("⚠️ Não consegui acessar a API da B3. Usando CDI real: 14.90%")
        return 14.90

cdi = buscar_cdi()

# --- EXIBE O CDI ---
st.info(f"""
📈 **CDI atual (12 meses): {cdi:.3f}%**
""")

# --- SIMULADOR DE GANHO LÍQUIDO ---
st.markdown("---")
st.subheader("💰 Simulador de Ganho Líquido (1, 2 ou 3 anos)")

valor = st.number_input("Quanto você quer aplicar? (R$)", min_value=1000, value=50000, step=1000)
prazo_anos = st.slider("Prazo da aplicação:", min_value=1, max_value=3, value=1, step=1)

resultados = []

for oferta in ofertas:
    nome = oferta['nome']
    tipo = oferta['tipo']
    rentabilidade_str = oferta['rentabilidade']
    isencao_ir = oferta['isencao_ir']

    # Extrai a taxa
    taxa_base = float(rentabilidade_str.replace("% CDI", "")) / 100

    if tipo == "CDB":
        ir_aliquota = 0.225 if valor > 20000 else 0.15
        ganho_bruto = valor * ((1 + taxa_base * cdi / 100) ** prazo_anos - 1)
        ganho_liquido = ganho_bruto * (1 - ir_aliquota)
        ir_pago = ganho_bruto * ir_aliquota
    elif tipo == "LCI" or tipo == "LCA":
        ir_aliquota = 0
        ganho_bruto = valor * ((1 + taxa_base * cdi / 100) ** prazo_anos - 1)
        ganho_liquido = ganho_bruto
        ir_pago = 0

    total_final = valor + ganho_liquido

    resultados.append({
        "Nome": nome,
        "Tipo": tipo,
        "Rentabilidade": rentabilidade_str,
        "Isento de IR?": isencao_ir,
        "Ganho Líquido": ganho_liquido,
        "IR Pago": ir_pago,
        "Total Final": total_final
    })

# --- MOSTRA RESULTADOS ---
df_resultados = pd.DataFrame(resultados)
df_resultados = df_resultados.sort_values(by="Ganho Líquido", ascending=False)

st.dataframe(
    df_resultados[
        ["Nome", "Tipo", "Rentabilidade", "Isento de IR?", "Ganho Líquido", "IR Pago", "Total Final"]
    ].style.format({
        "Ganho Líquido": "R$ {:,.2f}",
        "IR Pago": "R$ {:,.2f}",
        "Total Final": "R$ {:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

# --- MELHOR OPÇÃO ---
melhor = df_resultados.iloc[0]
st.success(f"""
✅ **MELHOR OPÇÃO PARA {prazo_anos} ANOS:**  
**{melhor['Nome']} → Ganho líquido de R$ {melhor['Ganho Líquido']:,.2f}**
""")

st.markdown("---")
st.caption("Projeto open source — construído com Python e Streamlit.")
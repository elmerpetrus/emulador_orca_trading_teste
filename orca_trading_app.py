import streamlit as st
import json
import requests
import time
import threading
from decimal import Decimal
import random
import subprocess
from pathlib import Path

# API pública da Binance para obter preços reais das criptomoedas
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price?symbol={}"

# Lista de tokens suportados (carregados do SDK do Orca So)
TOKEN_MAP = {
    "SOL": "SOLUSDT",
    "USDC": "USDCUSDT",
    "USDT": "USDTUSDT",
    "mSOL": "MSOLUSDT",
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "RAY": "RAYUSDT",
    "ORCA": "ORCAUSDT",
    "SRM": "SRMUSDT",
    "FTT": "FTTUSDT"
}

# Simulação da carteira do usuário com saldo inicial de 5.000 SOL
user_wallet = {token: 5.0 for token in TOKEN_MAP.keys()}
user_wallet["SOL"] = 5000.0  # Define o saldo inicial correto para simulação

wallet_balance_usd = {}
previous_prices = {}

# Função para buscar preços reais da Binance
def get_market_price(symbol):
    try:
        response = requests.get(BINANCE_API_URL.format(symbol))
        data = response.json()
        return float(data["price"])
    except Exception as e:
        return {"error": str(e)}

# Função para atualizar saldo da carteira e verificar variação
def update_wallet_balance():
    global wallet_balance_usd, previous_prices
    wallet_balance_usd.clear()
    total_balance_usd = 0

    for token, symbol in TOKEN_MAP.items():
        price = get_market_price(symbol)

        if isinstance(price, dict) and "error" in price:
            continue  # Se houver erro, pula para a próxima moeda

        if token in previous_prices:
            previous_prices[token]["last_price"] = previous_prices[token]["current_price"]
        else:
            previous_prices[token] = {"last_price": price, "current_price": price}

        previous_prices[token]["current_price"] = price

        wallet_balance_usd[token] = user_wallet[token] * price
        total_balance_usd += wallet_balance_usd[token]

    wallet_balance_usd["TOTAL"] = total_balance_usd

# Interface gráfica do Streamlit
st.set_page_config(page_title="🐋 Orca So Trading Simulado", layout="wide")
st.title("🐋 Simulador de Trading e Swap Orca So")

# Exibir saldo total da carteira atualizado na parte superior da tela
st.subheader("💰 Saldo Atual da Carteira")
if "TOTAL" in wallet_balance_usd:
    st.markdown(f"<h2 style='text-align: center;'>💵 Total: ${wallet_balance_usd['TOTAL']:.2f}</h2>", unsafe_allow_html=True)
else:
    st.markdown("<h2 style='text-align: center;'>Carregando saldo...</h2>", unsafe_allow_html=True)

# Criando o retângulo para exibir os saldos com cores baseadas na variação
st.markdown("<div style='border: 2px solid #ccc; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)

for token, balance in wallet_balance_usd.items():
    if token != "TOTAL":
        price_color = "green" if previous_prices[token]["current_price"] > previous_prices[token]["last_price"] else "red"
        st.markdown(
            f"<span style='color:{price_color}; font-size:16px;'><b>{token}:</b> {user_wallet[token]:.6f} ({balance:.2f} USD)</span>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# Interface para visualizar cotações reais de duas criptos
st.subheader("📊 Cotações de Mercado (Tempo Real)")
crypto1 = st.selectbox("Escolha a primeira criptomoeda", list(TOKEN_MAP.keys()), index=0)
crypto2 = st.selectbox("Escolha a segunda criptomoeda", list(TOKEN_MAP.keys()), index=1)

if st.button("Atualizar Cotações"):
    price1 = get_market_price(TOKEN_MAP[crypto1])
    price2 = get_market_price(TOKEN_MAP[crypto2])

    if isinstance(price1, dict) or isinstance(price2, dict):
        st.error("⚠️ Erro ao buscar cotações. Tente novamente mais tarde.")
    else:
        st.success(f"💰 Preço Atual: {crypto1} = ${price1:.2f}, {crypto2} = ${price2:.2f}")

# Área de Trading Simulado
st.subheader("🔄 Executar Trading Simulado / Conversão de Moeda")

token_from = st.selectbox("Criptomoeda Atual (Saldo Disponível)", list(TOKEN_MAP.keys()), index=0)
token_to = st.selectbox("Converter para", list(TOKEN_MAP.keys()), index=1)
amount = st.number_input("Quantidade a Converter", min_value=0.000001, format="%.6f")

if st.button("Executar Trading Simulado"):
    trade_result = {
        "status": "success",
        "converted": f"{amount} {token_from} → {Decimal(amount) * Decimal(get_market_price(TOKEN_MAP[token_from])) / Decimal(get_market_price(TOKEN_MAP[token_to])):.6f} {token_to}",
        "transaction_id": f"sim-trade-{random.randint(1000, 9999)}"
    }
    user_wallet[token_from] -= amount
    user_wallet[token_to] += float(Decimal(amount) * Decimal(get_market_price(TOKEN_MAP[token_from])) / Decimal(get_market_price(TOKEN_MAP[token_to])))
    
    update_wallet_balance()
    st.success(f"✅ {trade_result['converted']} - ID: {trade_result['transaction_id']}")

st.markdown("---")
st.markdown("🐋 **Simulador de Smart Contracts Orca So**")

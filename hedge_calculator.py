import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculate_hedge_bet(stake_a, odds_a, odds_b):
    """Calculate hedge bet amount and possible profits."""
    if odds_b <= 1:
        return 0, 0, 0, 0  # Prevent division errors
    
    hedge_bet = (stake_a * odds_a) / odds_b  # Ensures balance for profit
    payout_a = stake_a * odds_a
    payout_b = hedge_bet * odds_b
    
    profit_a = payout_a - (stake_a + hedge_bet)
    profit_b = payout_b - (stake_a + hedge_bet)
    
    min_hedge_odds = payout_a / stake_a if stake_a > 0 else 0
    return hedge_bet, profit_a, profit_b, min_hedge_odds

def calculate_ev(odds, stake):
    """Calculate Expected Value (EV) based on implied probability."""
    implied_prob = 1 / odds
    payout = stake * odds
    return (payout * implied_prob) - stake

# Streamlit UI Setup
st.title("🎯 Simple Hedge Betting Calculator 🎯")

# User Inputs
st.sidebar.header("🏦 Your Available Bankroll")
fd_balance = st.number_input("💰 Money in FanDuel ($)", min_value=0.0, value=260.0, step=1.0)
dk_balance = st.number_input("💰 Money in DraftKings ($)", min_value=0.0, value=200.0, step=1.0)

deposit_book = st.radio("📍 Where did you place your first bet?", ("FanDuel (FD)", "DraftKings (DK)"))
hedge_book = "DraftKings (DK)" if deposit_book == "FanDuel (FD)" else "FanDuel (FD)"
st.sidebar.write(f"📢 You will place the hedge bet on: **{hedge_book}**")

team_a_odds = st.slider("🎲 Select odds for Team A (the team you already bet on)", 1.01, 10.0, 2.0)
team_b_odds = st.slider("🎲 Select odds for Team B (the hedge bet team)", 1.01, 10.0, 2.0)

stake_a = st.number_input("💵 How much have you already bet on Team A? ($)", min_value=1.0, value=50.0, step=1.0)

# Calculate hedge bet and profits
hedge_bet, profit_a, profit_b, min_hedge_odds = calculate_hedge_bet(stake_a, team_a_odds, team_b_odds)

# Ensure available balance is correct
available_balance = dk_balance if hedge_book == "DraftKings (DK)" else fd_balance

# Beginner Mode
beginner_mode = st.sidebar.checkbox("🆕 Enable Beginner Mode")
if beginner_mode:
    st.info("📌 Step 1: Enter your bankroll.")
    st.info("📌 Step 2: Select your odds.")
    st.info("📌 Step 3: Enter your bet amount.")
    st.info("📌 Step 4: View suggested hedge bet and guaranteed profit.")

# Tabs for different features
tab1, tab2, tab3 = st.tabs(["📊 Risk-Free Profit", "💰 Maximize Profit", "📜 Bet History"])

with tab1:
    st.header("📊 Risk-Free Profit Calculation")
    arbitrage_condition = (1 / team_a_odds) + (1 / team_b_odds) < 1
    if arbitrage_condition:
        adjusted_hedge_bet = min(hedge_bet, available_balance)
        adjusted_profit_a = (stake_a * team_a_odds) - (stake_a + adjusted_hedge_bet)
        adjusted_profit_b = (adjusted_hedge_bet * team_b_odds) - (stake_a + adjusted_hedge_bet)
        risk_free_profit = min(adjusted_profit_a, adjusted_profit_b)
        
        if risk_free_profit > 0.01:
            st.success(f"✅ **Risk-Free Arbitrage Opportunity!** 🎉 Guaranteed Profit: **${risk_free_profit:.2f}**")
            st.write(f"💰 Adjusted Hedge Bet: **${adjusted_hedge_bet:.2f}** on {hedge_book}")
        else:
            st.warning("⚠️ Adjust bets or odds for a better arbitrage profit.")
    else:
        st.warning("⚠️ **No risk-free arbitrage detected.** Consider adjusting the odds or bet amount.")

with tab2:
    st.header("💰 Maximize Profit Strategy")
    custom_hedge = st.slider("💵 Adjust Hedge Bet Amount", 0.0, available_balance, hedge_bet)
    profit_a_custom = (stake_a * team_a_odds) - (stake_a + custom_hedge)
    profit_b_custom = (custom_hedge * team_b_odds) - (stake_a + custom_hedge)
    st.write(f"📊 **Adjusted Profit (if Team A wins):** ${profit_a_custom:.2f}")
    st.write(f"📊 **Adjusted Profit (if Team B wins):** ${profit_b_custom:.2f}")

with tab3:
    st.header("📜 Bet History")
    if "bet_history" not in st.session_state:
        st.session_state.bet_history = []
    if st.button("📜 Save This Bet"):
        st.session_state.bet_history.append({
            "Team A Odds": team_a_odds,
            "Team B Odds": team_b_odds,
            "Hedge Bet": hedge_bet,
            "Profit A": profit_a,
            "Profit B": profit_b
        })
    st.subheader("📊 Previous Bets")
    st.table(st.session_state.bet_history)
    
    # Export Bet History
    if st.button("📥 Export Bet History as CSV"):
        if st.session_state.bet_history:
            df = pd.DataFrame(st.session_state.bet_history)
            df.to_csv("bet_history.csv", index=False)
            st.success("✅ Bet history saved as 'bet_history.csv'")
        else:
            st.warning("⚠️ No bets to export.")

# 🤖 AI Vision Trading Agent

Autonomous On-Chain Asset Manager that utilizes Generative AI to analyze market charts and execute trades on the Mantle network.

## 🚀 Overview
The **AI Vision Agent** is an autonomous trading system that bridges the gap between decentralized finance (DeFi) and visual AI analysis. Unlike traditional trading bots that rely solely on lagging indicators, our agent uses computer vision to evaluate **Price Action** in real-time.

## 🛠 Features
- **Visual AI Analysis:** Uses Google Gemini (multimodal) to interpret candlestick patterns and support/resistance levels.
- **Autonomous Execution:** Executes on-chain transactions (Wrap/Unwrap) directly on the Mantle network using Web3.py.
- **Risk Management:** Built-in Stop Loss and Take Profit logic to remove human emotional bias.
- **Telegram Reporting:** Real-time trade reports, chart snapshots, and status updates sent directly to your mobile device.

## 🏗 Architecture


- **Data Layer:** Fetches live market data from Bybit and generates professional technical charts.
- **Brain Layer:** Google Gemini (Flash model) analyzes the visual state of the market.
- **Execution Layer:** Secure interaction with Mantle blockchain smart contracts.

## ⚙️ Setup

### 1. Requirements
- Python 3.10+
- Web3.py
- Google Generative AI SDK
- Pandas & Mplfinance

### 2. Configuration
Create a `.env` file in the project root:
``env
PRIVATE_KEY=your_wallet_private_key
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

3. Execution
Run the agent:
python main_bot.py

🔐 Security
Private keys are managed via environment variables.

Git ignores the .env file to prevent credential leakage.

🎯 Future Roadmap
Integration with DEX Routers (Uniswap V2/V3 interface) for real asset swaps.

Multi-asset portfolio management.

Dynamic Gas Price optimization.



GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

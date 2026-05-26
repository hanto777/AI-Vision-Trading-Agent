import requests
import pandas as pd
import mplfinance as mpf

def get_market_data(symbol="MNTUSDT", interval="15", limit=50):
    """Fetches the latest 50 candles"""
    print(f"📡 Fetching market data for {symbol}...")
    url = "https://api.bybit.com/v5/market/kline"
    params = {"category": "linear", "symbol": symbol, "interval": interval, "limit": limit}
    
    response = requests.get(url, params=params).json()
    if response['retCode'] != 0:
        print("❌ API Error:", response['retMsg'])
        return None

    data = response['result']['list']
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # mplfinance requires datetime index
    df.set_index('timestamp', inplace=True)
    
    return df

def calculate_levels_and_draw(df):
    """Calculates support/resistance and saves chart image"""
    print("🧮 Calculating technical levels and generating chart...")
    
    support = df['low'].min()
    resistance = df['high'].max()
    current_price = df['close'].iloc[-1]
    
    # Chart settings (Green = Support, Red = Resistance)
    apdict = [
        mpf.make_addplot([support]*len(df), color='g', linestyle='--', width=1.5),
        mpf.make_addplot([resistance]*len(df), color='r', linestyle='--', width=1.5)
    ]
    
    # Draw and save
    print("📸 Saving chart snapshot to chart.png...")
    mpf.plot(df, type='candle', style='charles', addplot=apdict, 
             title="MNT/USDT AI Vision Feed", volume=False, savefig='chart.png')
    
    return support, resistance, current_price

# --- Standalone Test ---
if __name__ == "__main__":
    df = get_market_data()
    if df is not None:
        support, resistance, current_price = calculate_levels_and_draw(df)
        print("\n=== 📊 MARKET ANALYSIS ===")
        print(f"Current Price: ${current_price:.4f}")
        print(f"Resistance:    ${resistance:.4f}")
        print(f"Support:       ${support:.4f}")
        print("✅ Chart successfully saved to chart.png")
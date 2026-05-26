import os
import time
import requests
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv

import step1_data
import step3_trade 
import step4_sell

# Загружаем ключи из .env файла
load_dotenv()

# --- KEYS SETUP ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# ---------------------------------------------

# ---------------------------------------------

genai.configure(api_key=GEMINI_API_KEY)
CHART_FILENAME = 'chart.png'

# --- RISK MANAGEMENT SETTINGS ---
STOP_LOSS_PCT = 0.02   # 2% стоп-лосс (продажа при падении на 2% от цены входа)
TAKE_PROFIT_PCT = 0.04 # 4% тейк-профит (продажа при росте на 4% от цены входа)

def send_telegram_alert(text, image_path=None):
    print("[Telegram] Sending report...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
    try:
        if image_path:
            with open(image_path, 'rb') as photo:
                requests.post(url + 'sendPhoto', data={'chat_id': TELEGRAM_CHAT_ID, 'caption': text, 'parse_mode': 'HTML'}, files={'photo': photo})
        else:
            requests.post(url + 'sendMessage', data={'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'HTML'})
    except Exception as e:
        print(f"[Error] Telegram alert failed: {e}")

def get_vision_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "flash" in m.name and "robotics" not in m.name:
                return genai.GenerativeModel(m.name)
    return genai.GenerativeModel('gemini-pro')

def ask_ai_for_visual_decision(model, current_price):
    try:
        img = PIL.Image.open(CHART_FILENAME)
        prompt = f"""
        Analyze this 15-minute MNT/USDT chart. 
        Current price: ${current_price:.4f}.
        Red line = Resistance, Green line = Support.
        
        Evaluate the visual pattern near the GREEN support line. Is there a strong bounce or rejection?
        Respond STRICTLY with ONE word: "BUY" or "WAIT". No explanations.
        """
        response = model.generate_content([prompt, img])
        return response.text.strip().upper()
    except Exception as e:
        print(f"[Error] Vision analysis failed: {e}")
        return "WAIT"

def run_agent():
    print("=== 🤖 AI VISION TRADING AGENT (PRODUCTION MODE) ===")
    model = get_vision_model()
    
    # СТАРТОВЫЕ ПЕРЕМЕННЫЕ (Бот начинает работу без открытых сделок)
    in_position = False
    entry_price = 0.0
    
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Waking up for market analysis...")
        
        df = step1_data.get_market_data(symbol="MNTUSDT", interval="15")
        if df is not None:
            support, resistance, current_price = step1_data.calculate_levels_and_draw(df)
            
            tg_message = f"🤖 <b>AI Agent Update</b>\n"
            
            # ЛОГИКА ЕСЛИ МЫ НЕ В СДЕЛКЕ (Ищем точку входа)
            if not in_position:
                tg_message += f"📊 Price: ${current_price:.4f}\n"
                decision = ask_ai_for_visual_decision(model, current_price)
                print(f"💡 AI Verdict: {decision}")
                tg_message += f"👁️ AI Decision: {decision}\n\n"
                
                if "BUY" in decision:
                    print("⚡ Executing BUY...")
                    step3_trade.execute_wrap() 
                    in_position = True
                    entry_price = current_price
                    tg_message += f"✅ <b>Action:</b> BUY executed at ${entry_price:.4f}\n"
                else:
                    print("⏳ Waiting for setup...")
                    tg_message += "⏳ <b>Action:</b> Searching for entry."
                    
            # ЛОГИКА ЕСЛИ МЫ УЖЕ В СДЕЛКЕ (Следим за позицией)
            else:
                print(f"📈 Holding position. Entry: ${entry_price:.4f} | Current: ${current_price:.4f}")
                
                tg_message += f"📊 Current Price: ${current_price:.4f}\n"
                tg_message += f"💼 <b>Position Active</b> (Entry: ${entry_price:.4f})\n\n"
                
                # Проверяем Stop Loss
                if current_price <= entry_price * (1 - STOP_LOSS_PCT):
                    print("🚨 STOP LOSS HIT! Selling...")
                    step4_sell.execute_unwrap()
                    in_position = False # Сбрасываем позицию
                    entry_price = 0.0
                    tg_message += f"🛑 <b>Action:</b> STOP LOSS hit. Position closed at ${current_price:.4f}."
                    
                # Проверяем Take Profit
                elif current_price >= entry_price * (1 + TAKE_PROFIT_PCT):
                    print("💰 TAKE PROFIT HIT! Selling...")
                    step4_sell.execute_unwrap()
                    in_position = False # Сбрасываем позицию
                    entry_price = 0.0
                    tg_message += f"🎯 <b>Action:</b> TAKE PROFIT hit. Position closed at ${current_price:.4f}."
                    
                else:
                    print("⚖️ Price is within safe zone. Holding.")
                    current_pnl = ((current_price - entry_price) / entry_price) * 100
                    tg_message += f"⚖️ <b>Action:</b> Holding. Current PnL: {current_pnl:.2f}%"

            send_telegram_alert(tg_message, CHART_FILENAME)
        
        print("💤 Sleeping for 15 minutes...")
        time.sleep(900) # Реальный сон на 15 минут между проверками свечей

if __name__ == "__main__":
    try:
        run_agent()
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped manually.")
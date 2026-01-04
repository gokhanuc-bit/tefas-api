from flask import Flask, request, jsonify
from tefas import Crawler
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Finans API (Duzeltilmis Versiyon)</h1><p>TEFAS: /api/fund?code=TCA<br>Yahoo: /api/yahoo?symbol=THYAO.IS</p>"

# --- 1. TEFAS FONKSIYONU ---
@app.route('/api/fund', methods=['GET'])
def get_fund():
    code = request.args.get('code')
    start = request.args.get('start')
    end = request.args.get('end')

    if not code:
        return jsonify({"error": "Code parametresi gerekli"}), 400
    
    if not end: end = datetime.now().strftime("%Y-%m-%d")
    if not start: start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        crawler = Crawler()
        df = crawler.fetch(start=start, end=end, name=code, columns=["date", "price"])
        if df.empty: return jsonify({"message": "Veri bulunamadı"}), 404
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 2. YAHOO FINANCE FONKSIYONU (DUZELTILDI) ---
@app.route('/api/yahoo', methods=['GET'])
def get_yahoo():
    symbol = request.args.get('symbol') # Örn: AAPL veya THYAO.IS
    start = request.args.get('start')
    end = request.args.get('end')

    if not symbol:
        return jsonify({"error": "Symbol parametresi gerekli (Orn: THYAO.IS)"}), 400

    if not end: end = datetime.now().strftime("%Y-%m-%d")
    if not start: start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        # --- DEĞİŞİKLİK BURADA ---
        # yf.download yerine Ticker.history kullanıyoruz.
        # Bu yöntem tek hisse için 'Tuple' hatası vermez, temiz veri döner.
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end)
        
        if df.empty:
            return jsonify({"message": "Veri bulunamadı. BIST icin sonuna .IS eklediniz mi?"}), 404

        # Yahoo verisi index olarak Date tutar, onu sütuna çevirelim
        df = df.reset_index()
        
        # Tarih formatını (Datetime -> String) düzeltelim
        # Timezone bilgisini (varsa) temizleyip sadece YYYY-MM-DD yapıyoruz
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Sadece Tarih ve Kapanış fiyatını alalım
        # Not: Bazen sütun isimleri küçük harf olabilir diye garantiye alıyoruz
        if 'Close' in df.columns:
            df = df.rename(columns={'Date': 'date', 'Close': 'price'})
        elif 'close' in df.columns:
             df = df.rename(columns={'Date': 'date', 'close': 'price'})
             
        # Sadece ihtiyacımız olan sütunları seçip sözlüğe çevirelim
        result = df[['date', 'price']].to_dict(orient="records")
        
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Hata detayi: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()

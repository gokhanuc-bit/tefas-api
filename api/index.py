from flask import Flask, request, jsonify
from tefas import Crawler
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Finans API (TEFAS + Yahoo)</h1><p>TEFAS: /api/fund?code=TCA<br>Yahoo: /api/yahoo?symbol=THYAO.IS</p>"

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

# --- 2. YAHOO FINANCE FONKSIYONU (YENI) ---
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
        # Yahoo'dan veriyi çek
        df = yf.download(symbol, start=start, end=end, progress=False)
        
        if df.empty:
            return jsonify({"message": "Veri bulunamadı. BIST icin sonuna .IS eklediniz mi?"}), 404

        # Yahoo verisi biraz karmasik gelir, duzenleyelim:
        df = df.reset_index()
        # Tarihi string'e cevir
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        # Sadece Tarih ve Kapanis fiyatini alalim
        result = df[['Date', 'Close']].rename(columns={'Date': 'date', 'Close': 'price'}).to_dict(orient="records")
        
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()

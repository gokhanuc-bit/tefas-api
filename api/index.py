from flask import Flask, request, jsonify
from tefas import Crawler
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Tefas API - Tarihsel Veri Modu</h1>"

@app.route('/api/fund', methods=['GET'])
def get_fund():
    code = request.args.get('code')
    # Tarih parametrelerini al (Eğer verilmezse varsayılanları kullan)
    start = request.args.get('start')
    end = request.args.get('end')

    if not code:
        return jsonify({"error": "Code parametresi gerekli"}), 400
    
    # Bitiş tarihi verilmezse "Bugün" olsun
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    
    # Başlangıç tarihi verilmezse "30 gün öncesi" olsun
    if not start:
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        crawler = Crawler()
        # Vercel timeout'a düşmesin diye sütunları azaltıyoruz
        df = crawler.fetch(start=start, end=end, name=code, columns=["date", "price"])
        
        if df.empty:
             return jsonify({"message": "Veri bulunamadı"}), 404

        result = df.to_dict(orient="records")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()

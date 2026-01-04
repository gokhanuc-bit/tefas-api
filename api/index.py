from flask import Flask, request, jsonify
from tefas import Crawler
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/fund', methods=['GET'])
def get_fund():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Fon kodu (code) parametresi gerekli. Ornek: ?code=TCA"}), 400
    
    # Tarihleri ayarla (Son 30 gün)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        crawler = Crawler()
        # Veriyi çek (Sütun isimlerini netleştirelim)
        df = crawler.fetch(start=start_date, end=end_date, name=code, columns=["date", "price"])
        
        if df.empty:
             return jsonify({"message": "Veri bulunamadı veya fon kodu hatalı."}), 404

        # Pandas DataFrame'i JSON formatına çevir
        result = df.to_dict(orient="records")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel'in bu dosyayı çalıştırması için gerekli
if __name__ == '__main__':
    app.run()

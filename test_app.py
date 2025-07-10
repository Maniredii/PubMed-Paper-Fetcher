from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask is working!</h1><p>PubMed Paper Finder Web App is ready.</p>'

if __name__ == '__main__':
    print("Starting test Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)

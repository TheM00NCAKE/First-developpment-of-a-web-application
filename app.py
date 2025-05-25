from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():    
    return render_template("index.html")

@app.route('/a_propos')
def a_propos():
    return render_template('a_propos.html')

@app.route('/Documentation')
def Documentation():
    return render_template('Documentation.html')

@app.route('/Donnnées_indicateurs')
def Données_indicateurs():
    return render_template('Données_indicateurs.html')

@app.route('/Carte')
def CarteFranceTest():
    return render_template('Carte.html')

if __name__ == '__main__':
    app.run(debug=True)

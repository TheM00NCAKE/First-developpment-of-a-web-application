from flask import Flask, render_template
from Model import *

app = Flask(__name__)
headings = ("Code indicateur","Nom Service","Mode gestion","Code commune","Nom commmune","Type collectivité","Indicateur")
data = get_all_data()

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
    return render_template('Données_indicateurs.html',headings=headings, data=data)

if __name__ == '__main__':
    app.run(debug=True)

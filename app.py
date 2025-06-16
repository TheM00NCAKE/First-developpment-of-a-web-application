from flask import Flask, render_template, request
from Model import *

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

@app.route('/Données_indicateurs', methods=['GET'])
def Données_indicateurs():
    return render_template('Données_indicateurs.html', table="")

session=Session("","","","","")
@app.route('/Update_tableau', methods=['GET'])
def Update_tableau():
    search = request.args.get("search")
    zone = request.args.get("zone")
    annee = request.args.get("annee")
    service = request.args.get("service")
    Lservice = request.args.get("Lservice")
    session.update_valeurs(search,zone,annee,service,Lservice)
    try:
        return session.processus_tab_graphe()
    except Exception as e:
        return(f"Erreur lors du chargement des données : {e}")
    
if __name__ == '__main__':
   app.run(debug=True)

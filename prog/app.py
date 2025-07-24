from flask import Flask, render_template, session, request, jsonify
from Model import *
from pathlib import Path
#faire en sorte que les éléments comme la feuille de style et les images sont récupérés correctement
path = str((Path(__file__).parent).parent / 'templates') 
path2 = str((Path(__file__).parent).parent / 'static')
app = Flask(__name__, template_folder=path, static_folder=path2)
app.secret_key = 'la_cle_secrete'  
@app.route("/")
def index():    
    theme = session.get('theme', 'clair')
    return render_template("index.html",theme=theme)

@app.route("/dict_indicateurs_retourner")
def dict_indicateurs_retourner():
    return jsonify(docs_dicts.dict_indicateurs)

@app.route('/a_propos')
def a_propos():
    theme = session.get('theme', 'clair')
    return render_template('a_propos.html',theme=theme)

@app.route('/Documentation')
def Documentation():
    theme = session.get('theme', 'clair')
    return render_template('Documentation.html',theme=theme)

@app.route('/Données_indicateurs', methods=['GET'])
def Données_indicateurs():
    theme = session.get('theme', 'clair')
    return render_template('Données_indicateurs.html', table="", theme=theme)

sessions=Session("","","","","")
@app.route('/Update_tableau', methods=['GET'])
def Update_tableau():
    search = request.args.get("search")
    zone = request.args.get("zone")
    annee = request.args.get("annee")
    service = request.args.get("service")
    Lservice = request.args.get("Lservice")
    sessions.update_valeurs(search,zone,annee,service,Lservice)
    try:
        return sessions.processus_tab_graphe()
    except Exception as e:
        return(f"Erreur lors du chargement des données : {e}")

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    # Récupérer l'état actuel du thème
    current_theme = session.get('theme', 'clair')
    
    # Inverser le thème
    new_theme = 'sombre' if current_theme == 'clair' else 'clair'
    
    # Sauvegarder dans la session
    session['theme'] = new_theme
    
    return jsonify({'theme': new_theme})
    
if __name__ == '__main__':
   app.run(debug=True)

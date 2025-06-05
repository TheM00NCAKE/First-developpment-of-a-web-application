from flask import Flask, render_template, request
from Model import *
import sqlite3
import pandas as pd
from pretty_html_table import build_table

app = Flask(__name__)

def tableau(): 
    #Construit une table de données en fonction des choix de l'utilisateur
    cnx = sqlite3.connect('Indicateur_des_services.db')
    #requête qui permet de construire n'importe quel requête (provenant de soit Démographie, Honoraires ou Prescriptions) en fonction de paramètres
    requete = f"""
        SELECT * from Descriptif where code_indicateur="VP.177" limit 10;
    """
    df = pd.read_sql_query(requete, cnx)
    if df.empty:       #si la requête n'affiche rien, un message s'affiche pour confirmer à l'utilisateur que les données qu'il veut sélectionner n'existe pas
        x="<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
    else:
        x = build_table(df, color="blue_dark", padding="15px 20px", font_size="14px",text_align='center',even_bg_color="#e8e8e8",odd_bg_color="#f5f5f5",border_bottom_color="blue_dark")    #créer un tableau bleu claire plus joli avec la bibliothèque pretty_html_table
        y = {
            '<table': '<table id="tableau"',
            '<tr style="text-align: right;"': '<tr style="border: 1px solid #1f2f90;"',
            '<th style="background-color: #305496;' : '<th',
        }

        for cle, valeur in y.items():
            x = x.replace(cle, valeur)

    cnx.close()
    return x

def tableau_by_search(filtrage):
    #Construit une table de données en fonction des choix de l'utilisateur
    cnx = sqlite3.connect('Indicateur_des_services.db')
    #requête qui permet de construire n'importe quel requête (provenant de soit Démographie, Honoraires ou Prescriptions) en fonction de paramètres
    requete = f"""
        SELECT * from Descriptif where 
        code_indicateur LIKE ?
        OR code_service LIKE ?
        OR nom_service LIKE ?
        OR numero_siren LIKE ?
        OR mode_gestion LIKE ?
        OR code_commune LIKE ?
        OR numero_collectivite LIKE ?
        limit 10;
    """
    df = pd.read_sql_query(requete, cnx, params=(filtrage, filtrage, filtrage, filtrage, filtrage, filtrage, filtrage))
    if df.empty:       #si la requête n'affiche rien, un message s'affiche pour confirmer à l'utilisateur que les données qu'il veut sélectionner n'existe pas
        x="<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
    else:
        x = build_table(df, color="blue_dark", padding="15px 20px", font_size="14px",text_align='center',even_bg_color="#e8e8e8",odd_bg_color="#f5f5f5",border_bottom_color="blue_dark")    #créer un tableau bleu claire plus joli avec la bibliothèque pretty_html_table
        y = {
            '<table': '<table id="tableau"',
            '<tr style="text-align: right;"': '<tr style="border: 1px solid #1f2f90;"',
            '<th style="background-color: #305496;' : '<th',
        }

        for cle, valeur in y.items():
            x = x.replace(cle, valeur)

    cnx.close()
    return x   

@app.route("/")
def index():    
    return render_template("index.html")

@app.route('/a_propos')
def a_propos():
    return render_template('a_propos.html')

@app.route('/Documentation')
def Documentation():
    return render_template('Documentation.html')

@app.route('/Donnnées_indicateurs', methods=['GET'])
def Données_indicateurs():
    search = request.args.get("search")
    print(search)
    try:
        if search:
            data = tableau_by_search(filtrage=search)
        else:
            data = tableau()
        return render_template('Données_indicateurs.html', table=data)
    except Exception as e:
        data = []
        return(f"Erreur lors du chargement des données : {e}")
    
    

if __name__ == '__main__':
    app.run(debug=True)

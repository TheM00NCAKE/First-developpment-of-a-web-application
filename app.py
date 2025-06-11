from flask import Flask, render_template, request
from Model import *
import requests
import urllib.parse
import sqlite3
import pandas as pd
from pretty_html_table import build_table
import docs_dicts

app = Flask(__name__)

def tableau_start(): 
    cnx = sqlite3.connect('Indicateur_des_services.db')
    requete = f"""
        SELECT * from Descriptif limit 10;  
    """
    #soit on garde cette requête comme étant une "démo" du tableau, ou on l'enlève et y'a rien quand on est sur la page au début
    df = pd.read_sql_query(requete, cnx)
    cnx.close()
    return df

def tableau_by_search(filtrage,an,service,Lservice):
    cnx = sqlite3.connect('Indicateur_des_services.db')
    df_total=pd.DataFrame()
    #Notifier à l'utilisateur quand il choisi des infos tout simplement pas dispo sur l'API du tout (ANC>2017)
    if (filtrage.lower()=='assainissement non collectif' or filtrage in docs_dicts.ANC)and int(an)>2017:
        return "<h1 style='text-align:center'>Les ANC ne sont plus enregistrés à partir de 2018.</h1>"
    try :
        #requête qui permet de construire n'importe quel requête en fonction de paramètres
        requete = f"""
            SELECT code_indicateur,code_service, nom_service,numero_siren,mode_gestion,Descriptif.code_commune, nom_commune,numero_collectivite 
            from Descriptif join Commune on Descriptif.code_commune=Commune.code_commune where nom_service LIKE ? AND 
            (code_indicateur LIKE ?
            OR nom_commune LIKE ?
            OR code_service LIKE ?
            OR numero_siren LIKE ?
            OR mode_gestion LIKE ?
            OR Descriptif.code_commune LIKE ?
            OR numero_collectivite LIKE ?) limit 700;
        """
        df = pd.read_sql_query(requete, cnx, params=(Lservice,filtrage, filtrage, filtrage, filtrage, filtrage, filtrage, filtrage))
        
        if df.empty:
            return "<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
        #récupérer tt les codes communes de notre requête df
        liste = df['code_commune'].unique().tolist()
        #récupérer tt les couples de code_service et code_indicateur de façon unique. 
        #NB : Peut importe la commune, toute ligne possèdant le même couple de données ont les mêmes vals d'indicateur.
        liste_infos = df[['code_service','code_indicateur']].drop_duplicates().values.tolist()
        df['valeur'] = None
        #Le but est d'exécuter plusieurs URL pour récupérer les infos de TOUT. Problème : communes max par url : 200
        for element in range (0,len(liste),200):
            #On fait donc une liste de 200 communes à chaque fois et on les mets dans les URL. 
            codes=','.join(liste[element:element+200])
            #urllib.parse.quote permet de bien 'traduire' les ',' en %2C dans les URL (qui signifie les ',', mais sont pas sous forme de ',')
            url=f'https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes?annee={an}&code_commune={urllib.parse.quote(codes)}&format=json&size=1000&type_service={service}'
            reponse = requests.get(url)
            reponse2 = reponse.json()
            #{code service : {indicateur : valeur, indicateur:valeur...}} 
            data = {list(commune.values())[2][0]: list(commune.values())[5] for commune in reponse2['data']} 
            for ligne in liste_infos: 
                code_service = ligne[0]
                code_indicateur = ligne[1]
                if code_service in data and code_indicateur in data[code_service]:  #data[code_service] contient tt les clés vals de chaque indicateur 
                        #localise toutes les lignes qui cochent cette condition (concerne les services avec bcp de communes) et leur attribue la val de l'indicateur
                    df.loc[(df['code_service']==code_service) & (df['code_indicateur']==code_indicateur), 'valeur'] = data[code_service][code_indicateur]
            #ajout au fur et à mesure des infos sur df_total :D
            df_total = pd.concat([df_total,df])
        cnx.close()
        return df_total
    except Exception as e:
        return f'une erreur est survenue : {reponse2}. Mince alors...'

#même idée, mais là c'est quand on clique sur la map
def tableau_map_clique(zone_clique,an,service,Lservice):
    cnx = sqlite3.connect('Indicateur_des_services.db')
    df_total = pd.DataFrame()
    codes_communes=[]
    #conditions pour récupérer toutes les communes à afficher 
    try :
        if zone_clique in docs_dicts.dict_regions :
            for element in docs_dicts.dict_regions[zone_clique]:
                codes_communes.extend(docs_dicts.dict_depts.get(element, [])) # .get() évite les KeyError
        elif zone_clique in docs_dicts.dict_depts:
            codes_communes.extend(docs_dicts.dict_depts.get(zone_clique, [])) # .get() évite les KeyError
        else : 
            return "<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
        if codes_communes:
            truc = ','.join(['?'] * len(codes_communes))
                            #requête qui permet de construire n'importe quel requête (provenant de soit Démographie, Honoraires ou Prescriptions) en fonction de paramètres
            requete = f"""
            SELECT code_indicateur,code_service, nom_service,numero_siren,mode_gestion,Descriptif.code_commune, nom_commune,numero_collectivite from Descriptif join Commune on Descriptif.code_commune=Commune.code_commune where 
            Descriptif.code_commune in ({truc}) limit 3000;
            """
            df=pd.read_sql_query(requete, cnx, params=codes_communes)
        liste = df['code_commune'].unique().tolist()
        liste_infos = df[['code_service','code_indicateur']].drop_duplicates().values.tolist()
        df['valeur'] = None
        for element in range (0,len(liste),200):
            codes=','.join(liste[element:element+200])
            url=f'https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes?annee={an}&code_commune={urllib.parse.quote(codes)}&format=json&size=1000&type_service={service}'
            reponse = requests.get(url)
            reponse2 = reponse.json()
            data = {list(commune.values())[2][0]: list(commune.values())[5] for commune in reponse2['data']} #{code service : {indicateur : valeur, indicateur:valeur...}}
                # Ajout d'une colonne 'valeur' initialisée à None
                # Remplissage ligne par ligne
            for ligne in liste_infos: 
                code_service = ligne[0]
                code_indicateur = ligne[1]
                if code_service in data and code_indicateur in data[code_service]:  #data[code_service] contient tt les clés vals de chaque indicateur 
                        #print(code_service,code_indicateur,data[code_service][code_indicateur])
                    df.loc[(df['code_service']==code_service) & (df['code_indicateur']==code_indicateur), 'valeur'] = data[code_service][code_indicateur]
            df_total = pd.concat([df_total,df], ignore_index=True)
        cnx.close()
        return df_total
    except Exception as e :
        return(f"Erreur lors du chargement des données : {e}")
            
def test(search,tableau):
    if search in docs_dicts.dict_indicateurs.keys() or search in docs_dicts.dict_indicateurs.values():
        maxi=tableau['valeur'].max(skipna=True)
        mini=tableau['valeur'].min(skipna=True)
        moy=tableau['valeur'].mean(skipna=True)
        pourcent=(moy/maxi)*100
        return f"""<p>Ceci est un placeholder pour la jauge de l'indicateur {search} ! Voilà. La valeur maximum de cet indicateur est de {maxi}, et la valeur minimum est {mini}. 
        La moyenne sur ces données est de {moy}, à peu près {round(pourcent, 2)}% de la valeur maximale"""
    else :
        return "<p>rien à signaler...</p>"

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
    load=1
    search = request.args.get("search")
    zone = request.args.get("zone")
    annee = request.args.get("annee")
    service = request.args.get("service")
    Lservice = request.args.get("Lservice")
    test_indicateur=""
    try:
        if search:
            dtframe=tableau_by_search(search,annee,service,Lservice)
        elif zone:
            dtframe = tableau_map_clique(zone, annee,service,Lservice)
        else:
            load=0
            dtframe=tableau_start()
        if isinstance(dtframe,str):       #si la requête n'affiche rien, un message en str s'affiche
            return dtframe
        else:
            test_indicateur= test(search,dtframe)
            tableau = build_table(dtframe, color="blue_dark", padding="15px 20px", font_size="14px",text_align='center',even_bg_color="#e8e8e8",odd_bg_color="#f5f5f5",border_bottom_color="blue_dark")    #créer un tableau bleu claire plus joli avec la bibliothèque pretty_html_table
            change_css = {
                '<table': '<table id="tableau"',
                '<tr style="text-align: right;"': '<tr style="border: 1px solid #104c76;"',
                '<th style="background-color: #305496;' : '<th',
            }
            for cle, valeur in change_css.items():
                tableau = tableau.replace(cle, valeur)
        if load==1: 
            return tableau + "|" + test_indicateur
        else :
            return render_template('Données_indicateurs.html', table=tableau)
    except Exception as e:
        return(f"Erreur lors du chargement des données : {e}")
    
if __name__ == '__main__':
   app.run(debug=True)

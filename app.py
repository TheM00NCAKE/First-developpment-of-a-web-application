from flask import Flask, render_template, request
from Model import *
import requests
import urllib.parse
import sqlite3
import pandas as pd
import docs_dicts
import duckdb as duck
import math
import json

app = Flask(__name__)

def tableau_by_search(filtrage,an,zone,service,Lservice):
    cnx = sqlite3.connect('Indicateur_des_services.db')
    df_total=pd.DataFrame()
    frame=[]
    try :
        if filtrage and not zone:
        #Notifier à l'utilisateur quand il choisi des infos tout simplement pas dispo sur l'API du tout (ANC>2017)
            if (filtrage.lower()=='assainissement non collectif' or filtrage in docs_dicts.ANC)and int(an)>2017:
                return "<h1 style='text-align:center'>Les ANC ne sont plus enregistrés à partir de 2018.</h1>"
            #requête qui permet de construire n'importe quel requête en fonction de paramètres
            requete = f"""
                SELECT Descriptif.code_indicateur,code_service,nom_service,Descriptif.code_commune,nom_commune, numero_siren,mode_gestion,type_collectivite,unite from Descriptif join Commune on Descriptif.code_commune=Commune.code_commune
                join Indicateur on Descriptif.code_indicateur=Indicateur.code_indicateur join Collectivite on Descriptif.numero_collectivite = 
                Collectivite.numero_collectivite where 
                nom_service LIKE ? AND 
                (Descriptif.code_indicateur LIKE ?
                OR nom_indicateur LIKE ?
                OR nom_commune LIKE ?
                OR code_service LIKE ?
                OR numero_siren LIKE ?
                OR mode_gestion LIKE ?
                OR Descriptif.code_commune LIKE ?
                OR type_collectivite LIKE ?) limit 5000;
            """
            df = pd.read_sql_query(requete, cnx, params=(f"{Lservice}%",*[f"{filtrage}%"]*8)) 
            print(len(df))
        else :
            codes_communes=[]
            if zone in docs_dicts.dict_regions :
                for element in docs_dicts.dict_regions[zone]:
                    codes_communes.extend(docs_dicts.dict_depts.get(element, [])) # .get() évite les KeyError
            elif zone in docs_dicts.dict_depts:
                codes_communes.extend(docs_dicts.dict_depts.get(zone, [])) # .get() évite les KeyError
            else : 
                return "<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
            if codes_communes:
                truc = ','.join(['?'] * len(codes_communes))
                if filtrage and zone :
                    requete = f"""
                    SELECT Descriptif.code_indicateur,code_service,nom_service,Descriptif.code_commune,nom_commune, numero_siren,mode_gestion,type_collectivite,unite from Descriptif join Commune on Descriptif.code_commune=Commune.code_commune
                    join Indicateur on Descriptif.code_indicateur=Indicateur.code_indicateur join Collectivite on Descriptif.numero_collectivite = 
                    Collectivite.numero_collectivite where 
                    (nom_service LIKE ? AND Descriptif.code_commune in ({truc})) AND
                    (Descriptif.code_indicateur LIKE ?
                    OR nom_indicateur LIKE ?
                    OR nom_commune LIKE ?
                    OR code_service LIKE ?
                    OR mode_gestion LIKE ?
                    OR type_collectivite LIKE ?) limit 5000;
                """
                    df=pd.read_sql_query(requete, cnx, params=(f"{Lservice}%",*codes_communes,*[f"{filtrage}%"] * 6))
                else : 
                    requete = f"""
                    SELECT Descriptif.code_indicateur,code_service,nom_service,Descriptif.code_commune,nom_commune, numero_siren,mode_gestion,type_collectivite,unite from Descriptif join Commune on Descriptif.code_commune=Commune.code_commune
                    join Indicateur on Descriptif.code_indicateur=Indicateur.code_indicateur join Collectivite on Descriptif.numero_collectivite = 
                    Collectivite.numero_collectivite
                    where nom_service LIKE ? AND Descriptif.code_commune in ({truc}) limit 5000;"""
                    df=pd.read_sql_query(requete, cnx, params=(f"{Lservice}%",*codes_communes))
        if df.empty:
            return "<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
        #récupérer tt les codes communes de notre requête df
        liste = df['code_commune'].unique().tolist()
        #récupérer tt les couples de code_service et code_indicateur de façon unique. 
        #NB : Peut importe la commune, toute ligne possèdant le même couple de données ont les mêmes vals d'indicateur.
        liste_infos = df[['code_service','code_indicateur']].drop_duplicates().values.tolist()
        df.insert(column='valeur', loc=8,value=None)
        #Le but est d'exécuter plusieurs URL pour récupérer les infos de TOUT. Problème : communes max par url : 200
        l_liste_200_ou_1 = range(1) if filtrage in docs_dicts.dict_indicateurs.keys() or filtrage in docs_dicts.dict_indicateurs.values() else range (0,len(liste),200)
        for element in l_liste_200_ou_1 :
            #On fait donc une liste de 200 communes à chaque fois et on les mets dans les URL. 
            codes=','.join(liste[element:element+200])
            if filtrage in docs_dicts.dict_indicateurs.keys() or filtrage in docs_dicts.dict_indicateurs.values():
                url=f'https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes?annee={an}&format=json&size=5000&type_service={service}'
            else :
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
            frame.append(df)
        df_total = pd.concat(frame, ignore_index=True)
        cnx.close()
        return df_total
    except Exception as e:
        return f'une erreur est survenue : {e}. Mince alors...'

def jauge(search,tableau):
    if search in docs_dicts.dict_indicateurs.keys() or search in docs_dicts.dict_indicateurs.values():
        maxi=tableau['valeur'].max(skipna=True)
        mini=tableau['valeur'].min(skipna=True)
        if maxi!=mini:
            moy=tableau['valeur'].mean(skipna=True)
            val_comparaison=maxi-mini
            pourcent=((moy-mini)/val_comparaison)*100
            con = duck.connect()
            con.register('tableau', tableau)
            con.register('tab_reg', docs_dicts.tab_reg)
            resultat = con.execute("""select avg(valeur) as moyenne, region from tableau join tab_reg on
            tableau.code_commune=tab_reg.code_commune group by region""").fetchdf()
            print(resultat)
            con.close()
            return str(pourcent) 
        else :
            return "100"
    else :
        return ""


def constr_graphe(tableau,zone,search,service):
    con = duck.connect()
    con.register('tableau', tableau)
    con.register('tab_reg', docs_dicts.tab_reg)
    #si une zone est cliqué est qu'un indicateur est recherché dans la search bar, on group by département de la région. Si c'est un dept cliqué
    #alors y'aura juste la moyenne du departement (jsp si c'est une bonne idée tho)
    if (search in docs_dicts.dict_indicateurs.keys() or search in docs_dicts.dict_indicateurs.values()) and zone :
        groupe="departement"
    #si le mot clé un indicateur : alors le group by se fait sur la région. Le graphique de l'évolution de l'indicateur va aussi s'afficher
    elif (search in docs_dicts.dict_indicateurs.keys() or search in docs_dicts.dict_indicateurs.values()):
        groupe="region"
    else : 
        groupe="code_indicateur"
    resultat = con.execute(f"""
    select avg(valeur) as moyenne, unite, {groupe} from tableau join tab_reg on tableau.code_commune = tab_reg.code_commune
    group by {groupe}, unite""").fetchdf()
    noms = [f"{ligne[groupe]}_{ligne['unite']}" for _, ligne in resultat.iterrows()]
    vals = resultat['moyenne'].tolist()
    valeurs=[-1 if math.isnan(val) else val for val in vals]
    data = {"noms": noms,"valeurs": valeurs}
    if groupe=="region":
        evolution_data = {}
        for i in range(2008,2020):
            #dttemp va retourner une dataframe avec les bons params pour chaque année
            dttemp=tableau_by_search(search,i,zone,service,"")
            #on ignore les vals nuls dans le calcul de la moyenne
            valeurs = [v for v in dttemp['valeur'] if v is not None]
            moyenne = sum(valeurs) / len(valeurs) if valeurs.count(0)<len(valeurs) else 0 
            evolution_data[i] = moyenne
        #data est constitué de data{"nom":[...],"valeurs":[...],"evolution":{annee:valeur....}}
        data["evolution"] = evolution_data
    else:
        data["evolution"] = {"rien":"rien"}
    con.close()
            
    with open("static/graph_data_region.json", "w", encoding="utf-8") as f:
        json.dump({**data}, f, ensure_ascii=False, indent=2)

    print('c bon')
    con.close()


def recup_val():
    with open("static/graph_data_region.js", "r", encoding="utf-8") as f:
        return 

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

@app.route('/Update_tableau', methods=['GET'])
def Update_tableau():
    search = request.args.get("search")
    zone = request.args.get("zone")
    annee = request.args.get("annee")
    service = request.args.get("service")
    Lservice = request.args.get("Lservice")
    test_indicateur=""
    try:
        if search or zone:
            dtframe=tableau_by_search(search,annee,zone,service,Lservice)
        else:
            return "" + "|" + ""
        if isinstance(dtframe,str):       #si la requête n'affiche rien, un message en str s'affiche
            return dtframe
        else:
            constr_graphe(dtframe,zone,search,service)
            test_indicateur= jauge(search,dtframe)
            tableau=dtframe.to_html(classes="tableau",index=False)
            tableau = tableau.replace('<table ', '<table id="tableau" ') 
        return tableau + "|" + test_indicateur 
    except Exception as e:
        return(f"Erreur lors du chargement des données : {e}")
    
if __name__ == '__main__':
   app.run(debug=True)

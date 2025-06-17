import sqlite3
import requests
import urllib.parse
import pandas as pd
import docs_dicts
import duckdb as duck
import math
import json

class Session:
    #### constructeurs et setters ####
    def __init__(self,filtrage,annee,zone,service,Lservice):
        self.filtrage=filtrage
        self.annee=annee
        self.zone=zone
        self.service=service
        self.Lservice=Lservice
        self.maxi_jauge=0
        self.mini_jauge=0
        self.indicateur_actuel = None
        self.annee_actuelle = None
        self.moyenne=""
    
    def update_search(self,nouv_filtrage):
        self.filtrage=nouv_filtrage
    
    def update_zone(self,nouv_zone):
        self.zone=nouv_zone
    
    def update_annee(self,nouv_annee):
        self.annee=nouv_annee
    
    def update_service(self,nouv_service):
        self.service=nouv_service
    
    def update_Lservice(self,nouv_Lservice):
        self.Lservice=nouv_Lservice

    def update_valeurs(self, search,zone,annee,service,Lservice):
        self.update_search(search)
        self.update_zone(zone)
        self.update_annee(annee)
        self.update_service(service)
        self.update_Lservice(Lservice)
    
    def tableau_by_search(self):
        """
        Retourne une DataFrame en fonction des paramètres de filtrages que l'utilisateur a mis.
        Une requête va s'exécuter en fonction des filtres (zone cliquée ou pas, barre de filtrage utilisée ou pas, quel année etc)
        et elle gère les erreurs, si il y'a rien comme filtrage, ou si la requête échoue (pas de données).
        """
        cnx = sqlite3.connect('Indicateur_des_services.db')
        df_total=pd.DataFrame()
        frame=[]
        try :
            if self.filtrage and not self.zone:
            #Notifier à l'utilisateur quand il choisi des infos tout simplement pas dispo sur l'API du tout (ANC>2017)
                if (self.filtrage.lower()=='assainissement non collectif' or self.filtrage in docs_dicts.ANC)and int(self.annee)>2017:
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
                df = pd.read_sql_query(requete, cnx, params=(f"{self.Lservice}%",*[f"{self.filtrage}%"]*8)) 
            else :
                codes_communes=[]
                if self.zone in docs_dicts.dict_regions :
                    for element in docs_dicts.dict_regions[self.zone]:
                        codes_communes.extend(docs_dicts.dict_depts.get(element, [])) # .get() évite les KeyError
                elif self.zone in docs_dicts.dict_depts:
                    codes_communes.extend(docs_dicts.dict_depts.get(self.zone, [])) # .get() évite les KeyError
                else : 
                    return "<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
                if codes_communes:
                    truc = ','.join(['?'] * len(codes_communes))
                    if self.filtrage and self.zone :
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
                        df=pd.read_sql_query(requete, cnx, params=(f"{self.Lservice}%",*codes_communes,*[f"{self.filtrage}%"] * 6))
                    else : 
                        requete = f"""
                        SELECT Descriptif.code_indicateur,code_service,nom_service,Descriptif.code_commune,nom_commune, numero_siren,mode_gestion,type_collectivite,unite from Descriptif join Commune on Descriptif.code_commune=Commune.code_commune
                        join Indicateur on Descriptif.code_indicateur=Indicateur.code_indicateur join Collectivite on Descriptif.numero_collectivite = 
                        Collectivite.numero_collectivite
                        where nom_service LIKE ? AND Descriptif.code_commune in ({truc}) limit 5000;"""
                        df=pd.read_sql_query(requete, cnx, params=(f"{self.Lservice}%",*codes_communes))
            if df.empty:
                return "<h1 style='text-align:center'>Informations indisponibles dans notre base de données</h1>"
            #récupérer tt les codes communes de notre requête df
            liste = df['code_commune'].unique().tolist()
            #récupérer tt les couples de code_service et code_indicateur de façon unique. 
            #NB : Peut importe la commune, toute ligne possèdant le même couple de données ont les mêmes vals d'indicateur.
            liste_infos = df[['code_service','code_indicateur']].drop_duplicates().values.tolist()
            df.insert(column='valeur', loc=8,value=None)
            #Le but est d'exécuter plusieurs URL pour récupérer les infos de TOUT. Problème : communes max par url : 200
            l_liste_200_ou_1 = range(1) if (self.filtrage in docs_dicts.dict_indicateurs.keys() or self.filtrage in docs_dicts.dict_indicateurs.values()) and self.service else range (0,len(liste),200)
            for element in l_liste_200_ou_1 :
                #On fait donc une liste de 200 communes à chaque fois et on les mets dans les URL. 
                codes=','.join(liste[element:element+200])
                if (self.filtrage in docs_dicts.dict_indicateurs.keys() or self.filtrage in docs_dicts.dict_indicateurs.values()) and self.service:
                    url=f'https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes?annee={self.annee}&format=json&size=5000&type_service={self.service}'
                elif (self.filtrage in docs_dicts.dict_indicateurs.keys() or self.filtrage in docs_dicts.dict_indicateurs.values()):
                    this = df['nom_service'].iloc[0]
                    if this=='assainissement collectif':
                        self.service='AC'
                    elif this=='assainissement non collectif':
                        self.service='ANC'
                    else:
                        self.service='AEP'
                #urllib.parse.quote permet de bien 'traduire' les ',' en %2C dans les URL (qui signifie les ',', mais sont pas sous forme de ',')
                    url=f'https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes?annee={self.annee}&code_commune={urllib.parse.quote(codes)}&format=json&size=1000&type_service={self.service}'
                else:
                    url=f'https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes?annee={self.annee}&code_commune={urllib.parse.quote(codes)}&format=json&size=1000&type_service={self.service}'
                reponse = requests.get(url)
                reponse2 = reponse.json()
                #{code service : {indicateur : valeur, indicateur:valeur...}} 
                data = {info['codes_service'][0]: info['indicateurs'] for info in reponse2['data']}
                for ligne in liste_infos: 
                    code_service = int(ligne[0])
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

    def jauge(self,tableau):
        if self.filtrage in docs_dicts.dict_indicateurs.keys() or self.filtrage in docs_dicts.dict_indicateurs.values():
            maxi=tableau['valeur'].max(skipna=True)
            mini=tableau['valeur'].min(skipna=True)
            if self.zone=="":
                self.maxi_jauge=maxi
                self.mini_jauge=mini
            if maxi!=mini:
                moy=tableau['valeur'].mean(skipna=True)
                val_comparaison=maxi-mini
                pourcent=((moy-mini)/val_comparaison)*100
                self.moyenne=str(pourcent)
                return f"{self.moyenne}|{self.filtrage}"
            else :
                return f"100|{self.filtrage}"
        else :
            return ""


    def constr_graphe(self,tableau):
        con = duck.connect()
        con.register('tableau', tableau)
        con.register('tab_reg', docs_dicts.tab_reg)
        #si une zone est cliqué est qu'un indicateur est recherché dans la search bar, on group by département de la région. Si c'est un dept cliqué
        #alors y'aura juste la moyenne du departement (jsp si c'est une bonne idée tho)
        if (self.filtrage in docs_dicts.dict_indicateurs.keys() or self.filtrage in docs_dicts.dict_indicateurs.values()) and self.zone :
            groupe="departement"
        #si le mot clé un indicateur : alors le group by se fait sur la région. Le graphique de l'évolution de l'indicateur va aussi s'afficher
        elif (self.filtrage in docs_dicts.dict_indicateurs.keys() or self.filtrage in docs_dicts.dict_indicateurs.values()):
            groupe="region"
        else : 
            groupe="code_indicateur"
        resultat = con.execute(f"""
        select avg(valeur) as moyenne, unite, {groupe} from tableau join tab_reg on tableau.code_commune = tab_reg.code_commune
        group by {groupe}, unite""").fetchdf()
        nom_pas_filtrés = [f"{ligne[groupe]}_{ligne['unite']}" for _, ligne in resultat.iterrows()]
        vals = resultat['moyenne'].tolist()
        noms=[]
        valeurs=[]
        for index,val in enumerate(vals):
            if not math.isnan(val) :
                valeurs.append(val)
                noms.append(nom_pas_filtrés[index])
        data = {"noms": noms,"valeurs": valeurs}
        if groupe=="region" or groupe=="departement":
            evolution_data = {}
            evolution=Session(self.filtrage,self.annee,self.zone,self.service,self.Lservice)
            if tableau['nom_service'].iloc[0] == "assainissement non collectif":
                annee_fin=2018
            else :
                annee_fin=2020
            for i in range(2008,annee_fin):
                #dttemp va retourner une dataframe avec les bons params pour chaque année
                evolution.update_annee(i)
                dttemp=evolution.tableau_by_search()
                #on ignore les vals nuls dans le calcul de la moyenne
                valeurs = [v for v in dttemp['valeur'] if v is not None]
                moyenne = sum(valeurs) / len(valeurs) if valeurs.count(0)<len(valeurs) else 0 
                evolution_data[i] = moyenne
            #data est constitué de data{"nom":[...],"valeurs":[...],"evolution":{annee:valeur....}}
            data["evolution"] = evolution_data
            clr_zone={} 
            if self.maxi_jauge!=self.mini_jauge:
                val_comparaison=self.maxi_jauge-self.mini_jauge
                if groupe=="region":
                    self.indicateur_actuel=self.filtrage
                    self.annee_actuelle=self.annee
                for _, elmt in resultat.iterrows():
                    if pd.isna(elmt['moyenne']):
                        clr_zone[elmt[f'{groupe}']] = "rgb(213, 213, 218)"
                        continue
                    p=((elmt['moyenne']-self.mini_jauge)/val_comparaison)
                    # Rouge -> Jaune -> Vert
                    if p < 0.5:
                        # de rouge (255,0,0) à jaune (255,255,0)
                        red = 255
                        green = int(255 * (p / 0.5)) # de 0 à 255
                        blue = 0
                    else:
                        # de jaune (255,255,0) à vert (0,255,0)
                        red = int(510 * (1 - p))  # de 255 à 0
                        green = 255
                        blue = 0
                    clr_zone[elmt[f'{groupe}']]=f"rgb({red},{green},{blue})"
            elif self.mini_jauge==self.maxi_jauge and self.mini_jauge>0:
                for _, elmt in resultat.iterrows():
                    clr_zone[elmt[f'{groupe}']]=f"rgb(0,255,0)" 
            else : 
                for _, elmt in resultat.iterrows():
                    clr_zone[elmt[f'{groupe}']]=f"rgb(255,0,0)" 
            data['couleur_zone']=clr_zone
        else:
            data["evolution"] = {"rien":"rien"}
        con.close()
                
        with open("static/graph_data_region.json", "w", encoding="utf-8") as f:
            json.dump({**data}, f, ensure_ascii=False, indent=2)

        print('c bon')
        con.close()

    def processus_tab_graphe(self):
        test_indicateur=""
        try:
            if self.filtrage or self.zone:
                dtframe=self.tableau_by_search()
            else: #rien n'a été sélectionné, ou alors la barre de filtrage n'a rien
                return "" + "|" + ""
            if isinstance(dtframe,str):       #si la requête n'affiche rien, un message en str s'affiche
                return dtframe
            else:
                test_indicateur= self.jauge(dtframe)
                self.constr_graphe(dtframe)
                tableau=dtframe.to_html(classes="tableau",index=False)
                tableau = tableau.replace('<table ', '<table id="tableau" ') 
            return tableau + "|" + test_indicateur 
        except Exception as e:
            return(f"Erreur lors du chargement des données : {e}")

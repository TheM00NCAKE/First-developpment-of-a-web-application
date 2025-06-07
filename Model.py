import sqlite3

def connexion():
    try:
        return sqlite3.connect("Indicateur_des_services.db")
    except:
        print("Connexion impossible")

def create_table_Indicateur():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = '''CREATE TABLE IF NOT EXISTS Indicateur(
                        code_indicateur TEXT PRIMARY KEY,
                        nom_indicateur TEXT,
                        unite TEXT
                        );'''
           
            cursor.execute(sql)
            conn.commit()
    except Exception as e:
        print(f"Une erreur a été repéré pendant la création de la table: {e}")


def create_table_Commune():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = '''CREATE TABLE IF NOT EXISTS Commune(
                        code_commune INTEGER PRIMARY KEY,
                        nom_commune TEXT
                        );'''
           
            cursor.execute(sql)
            conn.commit()
    except Exception as e:
        print(f"Une erreur a été repéré pendant la création de la table: {e}")


def create_table_Collectivite():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = '''CREATE TABLE IF NOT EXISTS Collectivite(
                        numero_collectivite INTEGER PRIMARY KEY,
                        type_collectivite TEXT
                        );'''
           
            cursor.execute(sql)
            conn.commit()
    except Exception as e:
        print(f"Une erreur a été repéré pendant la création de la table: {e}")

def create_table_Descriptif():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = '''CREATE TABLE IF NOT EXISTS Descriptif(
                        code_indicateur TEXT,
                        code_service INTEGER,
                        nom_service TEXT,
                        numero_siren INTEGER,
                        mode_gestion TEXT,
                        code_commune INTEGER,
                        numero_collectivite INTEGER,
                        FOREIGN KEY (code_commune) REFERENCES Commune(code_commune),
                        FOREIGN KEY (numero_collectivite) REFERENCES Collectivite(numero_collectivite),
                        FOREIGN KEY (code_indicateur) REFERENCES Indicateur(code_indicateur),
                        PRIMARY KEY (code_indicateur, code_service)

                        );'''
           
            cursor.execute(sql)
            conn.commit()
    except Exception as e:
        print(f"Une erreur a été repéré pendant la création de la table: {e}")



def select_table(table):
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = f"SELECT * FROM {table};"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(f"Erreur lors de la sélection dans la table: {e}")
        return None

def update_row(table, column, new_value, condition_column, condition_value):
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = f"UPDATE {table} SET {column} = ? WHERE {condition_column} = ?;"
            cursor.execute(sql, (new_value, condition_value))
            conn.commit()
    except Exception as e:
        print(f"Erreur lors de la mise à jour dans : {e}")


def delete_row(table, column, value):
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = f"DELETE FROM {table} WHERE {column} = ?;"
            cursor.execute(sql, (value,))
            conn.commit()
    except Exception as e:
        print(f"Erreur lors de la suppression dans '{table}': {e}")

def get_all_data():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            # Requête SQL pour récupérer toutes les données
            sql = '''SELECT * FROM Descriptif'''
            cursor.execute(sql)
            conn.commit()
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(f"Erreur lors de la récupération des données de la table descriptif ou tout: {e}")
        return None



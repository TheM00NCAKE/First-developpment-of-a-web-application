from flask import Flask, render_template
import Indicateur_des_services.db as db

app = Flask(__name__)
headings = ("N° de ligne", "Code service","Année","Service","Mode gestion","Collectivité","Commune","Indicateur","Valeur","Unité")
data = (
    ("1","74893", "2019", "Service1", "A deux", "Commune", "Alfortville", "D102", "94", "%"),
    ("2","89426", "2018", "Service2", "Seul", "Plusieurs village" ,"Maison-Alfort" ,"VP.189" ,"4000" ,"m²"),
    ("3","35783", "2017", "Service3", "Seul", "Commune" ,"Paris" ,"D.109" ,"45" ,"€")
)

tableau = request.args.get("tableau", "Demographie")

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

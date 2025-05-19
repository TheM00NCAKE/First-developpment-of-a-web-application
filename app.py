from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/apropos')
def a_propos():
    return render_template('a_propos.html')

@app.route('/indice')
def indice():
    return render_template('indice.html')



if __name__ == '__main__':
    app.run(debug=True)

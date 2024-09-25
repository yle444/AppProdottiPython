import numpy as np
from flask import Flask, render_template, request, make_response  # importo flask
import mysql.connector  # importo il connettore
from flask import Flask, request, redirect, url_for, session
from matplotlib import pyplot as plt
import io
import pandas as pd #importo libreria pandas


# creo oggetto di tipo evento
class prodottoPets:
    def __init__(self, nome, marca, prezzo, categoria, url, pezzi, pezziVenduti):
        self.nome = nome
        self.marca = marca
        self.prezzo = prezzo
        self.categoria = categoria
        self.url = url
        self.pezzi = pezzi
        self.pezziVenduti = pezziVenduti

    def __str__(self):
        return f'{self.nome} {str(self.marca)} {str(self.prezzo)} {str(self.categoria)} {str(self.url)} {str(self.pezzi)} {str(self.pezziVenduti)}'


class pezziVenduti:
    def __init__(self, nome, marca, prezzo, url):
        self.nome = nome
        self.marca = marca
        self.prezzo = prezzo

        self.url = url

    def setPezzi(self, pezziV):
        self.pezziV = pezziV

    def getPezzi(self):
        return self.pezziV


# Variabili username e password predefinite
USERNAME = "admin"
PASSWORD = "password"

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Usato per firmare la sessione

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="PyDb"
)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica le credenziali dell'utente
        if username == USERNAME and password == PASSWORD:
            session['user'] = username  # Memorizza l'utente nella sessione
            return redirect(url_for('gestore'))  # Reindirizza all'area protetta
        else:
            return "Credenziali non valide"

    return render_template("login.html")


# Rotta accessibile solo dopo l'autenticazione
@app.route('/gestore')
def gestore():
    if 'user' in session:
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM prodottipets")


        myresult = mycursor.fetchall()
        listaD = []
        for i in myresult:
            listaD.append(i[4])  # metto l'indice corrispondente alla colonna che voglio(in questo case categoria)

        listaS = list(dict.fromkeys(listaD))
        print(listaS)
        import csv

        # Nome del file CSV
        file_csv = 'prodottiPets.csv'

        # Scrivi i dati nel file CSV
        with open(file_csv, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Scrivi l'intestazione (opzionale)
            writer.writerow(['ID', 'Nome', 'Marca', 'Prezzo', 'Categoria', 'URL', 'Pezzi',
                             'Pezzi venduti'])  # Modifica in base alle tue colonne

            # Scrivi i dati
            writer.writerows(myresult)

        print(f"File {file_csv} creato con successo!")

        #utilizzo libreria pandas per dati
        query = ("SELECT * FROM prodottipets")
        df = pd.read_sql(query, mydb)
        pd.set_option('display.max_columns', None)#non voglio nessuna limitazione colonne

        #print(df)#non mi visualizza tutta la tabella
        lista_prodotti = df.values.tolist()
        print(lista_prodotti)

        query = ("SELECT id,nome, marca, pezzi, pezziVenduti  FROM prodottipets")
        mycursor.execute(query)
        myresult1 = mycursor.fetchall()
        # Ottenere i nomi delle colonne
        column_names = [desc[0] for desc in mycursor.description]

        # Creare un DataFrame Pandas con i nomi delle colonne
        df = pd.DataFrame(myresult1, columns=column_names)
        print(df) #mi visualizza tutta la tabella
        sommaP = df['pezzi'].sum()
        sommaV = df['pezziVenduti'].sum()
        print("la somma dei pezzi è ", sommaP) #stampo la somma dei pezzi
        print("la somma dei pezzi venduti è ", sommaV) #stampo la somma dei pezzi venduti
        mediaP = df['pezzi'].mean()
        mediaV = df['pezziVenduti'].mean()
        print("la media dei pezzi è ", mediaP)
        print("la media dei pezzi venduti è ", mediaV)


        new_row = {
            'id': "",  # Imposta su NaN o su un valore predefinito
            'nome': "Somma",  # Imposta su NaN o su un valore predefinito
            'marca': "",  # Imposta su NaN o su un valore predefinito
            'pezzi': sommaP,  # Valore specificato
            'pezziVenduti': sommaV  # Valore specificato
        }



        new_row2 = {
            'id': "",  # Imposta su NaN o su un valore predefinito
            'nome': "Media",  # Imposta su NaN o su un valore predefinito
            'marca': "",  # Imposta su NaN o su un valore predefinito
            'pezzi': mediaP,  # Valore specificato
            'pezziVenduti': mediaV  # Valore specificato
        }

        ## Creare un DataFrame dalla nuova riga
        new_row_df = pd.DataFrame([new_row])
        new_row2_df = pd.DataFrame([new_row2])

        # Aggiungere la nuova riga usando pd.concat
        df = pd.concat([df, new_row_df], ignore_index=True)
        df = pd.concat([df, new_row2_df], ignore_index=True)

        lista_prodotti = df.values.tolist()
        print(lista_prodotti)

        # Calcolare il prodotto più venduto
        index_max = df['pezziVenduti'].idxmax()  # Ottieni l'indice del valore massimo

        # Calcolare l'indice del prodotto più venduto, escludendo le ultime 2 righe
        index_max = df['pezziVenduti'][:-2].idxmax()
        prodotto_piu_venduto = df.loc[index_max]
        prodottoMax = prodotto_piu_venduto['nome']
        print(prodottoMax)

        # Calcolare l'indice del prodotto meno venduto, escludendo le ultime 2 righe
        index_min = df['pezziVenduti'][:-2].idxmin()
        prodotto_meno_venduto = df.loc[index_min]
        prodottoMin = prodotto_meno_venduto['nome']
        print(prodottoMin)



        return render_template("gestore.html", listaP=lista_prodotti, lista=myresult, listaS=listaS, prodottoMax=prodottoMax, prodottoMin=prodottoMin)
    else:
        return redirect(url_for('login'))


@app.route('/process', methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        nome = request.form['nome']
        marca = request.form['marca']
        prezzo = request.form['prezzo']
        categoria = request.form['categoria']
        url = request.form['url']
        pezzi = request.form['pezzi']
        pezziVenduti = 0

        mycursor = mydb.cursor()

        sql = "INSERT INTO prodottipets (nome, marca, prezzo, categoria, url, pezzi, pezziVenduti) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (nome, marca, prezzo, categoria, url, pezzi, pezziVenduti)  # definiamo valori
        mycursor.execute(sql, val)  # eseguo la query
        mydb.commit()

        print(mycursor.rowcount, "record inserted.")
        p1 = prodottoPets(nome, marca, prezzo, categoria, url, pezzi, pezziVenduti)

        return render_template("dettagliProdottoIns.html", prod=p1)


@app.route('/remove', methods=['POST', 'GET'])
def remove():
    if request.method == 'POST':
        id = int(request.form['prod'])
        mycursor = mydb.cursor()

        sql = "DELETE FROM prodottipets WHERE id=%s"
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record removed.")  # il cursore ritorna un numero
        # return (gestore())
        return ("prodotto rimosso")


@app.route('/ricerca', methods=['POST', 'GET'])
def ricerca():
    if request.method == 'POST':
        categoria = (request.form['categoria'])
        mycursor = mydb.cursor()

        sql = "SELECT * FROM prodottipets WHERE categoria=%s"
        val = (categoria,)
        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()

        return render_template("listaProdotti.html", lista=myresult)


lista = []


@app.route("/")
def store():
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM prodottipets")

    myresult = mycursor.fetchall()

    totCarrello = 0
    for i in lista:
        totCarrello += int(i.prezzo) * int(i.getPezzi())

    return render_template("store.html", lista=myresult, carrello=lista, totale=totCarrello)


@app.route("/updatePezzi", methods=['POST', 'GET'])
def updatePezzi():
    if request.method == 'POST':
        id = int(request.form['prodID'])
        pezzi = request.form['numPezzi']
        mycursor = mydb.cursor()
        sql = "UPDATE prodottipets SET pezzi = pezzi + %s  WHERE id = %s"
        val = (pezzi, id)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record update.")
        # return (gestore())
        return ("Prodotto aggiornato")


@app.route("/buy", methods=['POST', 'GET'])
def buy():
    if request.method == 'POST':

        for i, p1 in enumerate(lista):
            mycursor = mydb.cursor()
            sql = "UPDATE prodottipets SET pezzi = pezzi - %s  WHERE nome = %s"
            val = (p1.getPezzi(), p1.nome)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")

            mycursor = mydb.cursor()
            sql = "UPDATE prodottipets SET pezziVenduti = pezziVenduti + %s  WHERE nome = %s"
            val = (p1.getPezzi(), p1.nome)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")


    somma = 0
    for i in lista:
        somma += int(i.prezzo) * int(i.getPezzi())
    return render_template("recap.html", lista=lista, somma=somma)


@app.route("/add", methods=['POST', 'GET'])
def add():
    id = request.form.get('prodId')
    num = request.form.get('prodA')

    mycursor = mydb.cursor()

    sql = ("SELECT * FROM prodottipets WHERE id = %s")

    val = (id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    for p1 in myresult:
        p2 = pezziVenduti(p1[1], p1[2], p1[3], p1[5])
        p2.setPezzi(num)
        lista.append(p2)

    return (store())


@app.route("/rimuovi", methods=['POST', 'GET'])
def rimuovi():
    if request.method == 'POST':
        nome = request.form['nome']

        for p1 in lista:
            if (p1.nome == nome):
                lista.remove(p1)

    return (store())


@app.route('/combined_chart.png')
def plot_png():
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM prodottipets")

    prodotti = mycursor.fetchall()

    # Estrai le etichette (colonna [1]) e vendite (colonna [7]) dalle tuple
    etichette = [row[1] for row in prodotti]  # Supponiamo che row[1] sia il nome del prodotto
    vendite = [row[6] for row in prodotti]  # Sup

    # Crea una figura con due subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 5))  # 1 riga, 2 colonne

    # --- Grafico a barre ---
    ax1.bar(etichette, vendite, color='skyblue')
    ax1.set_title('Vendite per Prodotto (Grafico a Barre)')
    ax1.set_ylabel('Vendite')

    # --- Grafico a torta ---
    ax2.pie(vendite, labels=etichette, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99'])
    ax2.axis('equal')  # Per mantenere la torta circolare
    ax2.set_title('Distribuzione Vendite (Grafico a Torta)')

    # Salva la figura in memoria come PNG
    output = io.BytesIO()
    fig.savefig(output, format='png')
    plt.close(fig)
    output.seek(0)

    return make_response(output.getvalue(), 200, {'Content-Type': 'image/png'})
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# Fonction pour lire le fichier CSV
def lire_Colloscope_G11():
    return pd.read_csv('Colloscope_G11.csv', encoding='utf-8')

# Fonction pour obtenir le programme d'une semaine donnée
def obtenir_programme_semaine(semaine_a_afficher):
    programme = lire_Colloscope_G11()
    programme_semaine = programme[programme['Semaine'] == semaine_a_afficher]
    return programme_semaine

# Fonction pour vérifier si une semaine existe dans le CSV
def verifier_semaine_existe(semaine):
    programme = lire_Colloscope_G11()
    return not programme[programme['Semaine'] == semaine].empty

@app.route('/')
@app.route('/<semaine>')
def afficher_programme(semaine=None):
    aujourd_hui = datetime.now()

    # Définir les périodes des vacances
    debut_vacances_toussaint = datetime(2024, 10, 21)
    fin_vacances_toussaint = datetime(2024, 11, 10)

    debut_vacances_noel = datetime(2024, 12, 14)
    fin_vacances_noel = datetime(2025, 1, 12)

    if semaine is None:
        # Si aucune semaine n'est spécifiée et qu'on est pendant les vacances, afficher la semaine suivante après les vacances
        if debut_vacances_toussaint <= aujourd_hui <= fin_vacances_toussaint:
            semaine = "11/11/24"
        elif debut_vacances_noel <= aujourd_hui <= fin_vacances_noel:
            semaine = "06/01/25"  # Afficher la semaine de la rentrée après Noël
        else:
            semaine = aujourd_hui.strftime('%d/%m/%y')

    # Décodage des dates au format URL-friendly
    semaine = semaine.replace('-', '/')  # Convertir les dates au format CSV (dd/mm/yy)

    try:
        programme_semaine = obtenir_programme_semaine(semaine)
        if programme_semaine.empty:
            raise ValueError("Pas de données pour la semaine spécifiée")
    except:
        # Si la semaine n'existe pas, revenir à une semaine par défaut
        semaine = "11/11/24"
        programme_semaine = obtenir_programme_semaine(semaine)

    tableau = programme_semaine.to_dict(orient='records')

    # Calculer la semaine suivante et précédente
    semaine_date = datetime.strptime(semaine, '%d/%m/%y')
    semaine_suivante = (semaine_date + timedelta(weeks=1)).strftime('%d-%m-%y')
    semaine_precedente = (semaine_date - timedelta(weeks=1)).strftime('%d-%m-%y')

    # Corriger la navigation des semaines pendant les vacances de Noël
    if semaine_date >= debut_vacances_noel and semaine_date <= fin_vacances_noel:
        semaine_suivante = "06-01-25"
        semaine_precedente = "16-12-24"

    # Corriger le passage à la semaine du 13/01/25
    if semaine == "06/01/25":
        semaine_suivante = "13-01-25"  # Forcer la semaine suivante après le 06/01/25
        semaine_precedente = "16-12-24"  # Corriger le retour en arrière vers 16/12/24

    elif semaine == "13/01/25":
        semaine_precedente = "06-01-25"
        semaine_suivante = "Pas de données"  # Pas de semaine suivante après le 13/01/25

    # Corriger la navigation arrière depuis la semaine du 16/12/24 vers 09/12/24
    if semaine == "16/12/24":
        semaine_precedente = "09-12-24"  # Corriger le retour en arrière depuis 16/12/24

    # Vérifier si la semaine suivante ou précédente existe dans le CSV
    if not verifier_semaine_existe(semaine_suivante.replace('-', '/')) and semaine_suivante != "Pas de données":
        semaine_suivante = "Pas de données"
    if not verifier_semaine_existe(semaine_precedente.replace('-', '/')) and semaine_precedente != "Pas de données":
        semaine_precedente = "Pas de données"

    # Logs pour vérifier les semaines actuelles et suivantes
    print(f"Semaine actuelle : {semaine}, Semaine suivante : {semaine_suivante}, Semaine précédente : {semaine_precedente}")

    return render_template('index.html', tableau=tableau, semaine=semaine.replace('/', '-'), semaine_suivante=semaine_suivante, semaine_precedente=semaine_precedente)

if __name__ == '__main__':
    app.run(debug=True)

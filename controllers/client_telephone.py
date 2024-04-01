#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, session, request
from connexion_db import get_db

client_telephone = Blueprint('client_telephone', __name__, template_folder='templates')

@client_telephone.route('/client/telephone/show')
def client_telephone_show():
    mycursor = get_db().cursor()

    # Modification de la requête pour agréger le stock par téléphone
    query = ('''
        SELECT telephone.id_telephone, telephone.libelle_telephone, telephone.poids_telephone, 
               telephone.stockage_telephone, telephone.prix_telephone, telephone.autonomie_telephone, 
               telephone.image_telephone, telephone.modele_id, COALESCE(SUM(declinaison.stock) , 0) as stock,
               COUNT(DISTINCT CONCAT(declinaison.couleur_id, '-', declinaison.taille_id)) as nb_declinaisons
        FROM telephone
        LEFT JOIN declinaison ON telephone.id_telephone = declinaison.telephone_id
        GROUP BY telephone.id_telephone
        ''')
    params = []

    if 'filter_word' in session and session['filter_word']:
        query += " AND libelle_telephone LIKE %s"
        params.append("%{}%".format(session['filter_word']))  # Corrected syntax and formatting

    if 'filter_prix_min' in session and session['filter_prix_min']:
        query += " AND prix_telephone >= %s"
        params.append(session['filter_prix_min'])

    if 'filter_prix_max' in session and session['filter_prix_max']:
        query += " AND prix_telephone <= %s"
        params.append(session['filter_prix_max'])

    if 'filter_types' in session and session['filter_types']:
        type_placeholders = ', '.join(['%s'] * len(session['filter_types']))  # Fixed syntax error
        if type_placeholders:
            query += " AND modele_id IN ({})".format(type_placeholders)
            params.extend(session['filter_types'])

    mycursor.execute(query, params)
    telephones = mycursor.fetchall()
    print(telephones)

    id_client = session['id_user']


    sql = "SELECT * FROM modele"
    mycursor.execute(sql)
    modele = mycursor.fetchall()
    """
    telephones_panier = []

    if len(telephones_panier) >= 1:
        sql = "calcul du prix total du panier"  # Replace with actual calculation logic
        prix_total = None
    else:
        prix_total = None
    """


    sql = "SELECT telephone.libelle_telephone, telephone.prix_telephone, ligne_panier.quantite, telephone.id_telephone FROM ligne_panier JOIN telephone ON ligne_panier.declinaison_id = telephone.id_telephone WHERE ligne_panier.utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    telephones_panier = mycursor.fetchall()

    prix_total = sum(item['quantite'] * item['prix_telephone'] for item in telephones_panier)

    return render_template('client/boutique/panier_telephone.html',
                           telephones=telephones,
                           telephones_panier=telephones_panier,
                           items_filtre=modele,
                           prix_total=prix_total)


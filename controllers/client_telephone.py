#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, session, request
from connexion_db import get_db

client_telephone = Blueprint('client_telephone', __name__, template_folder='templates')


@client_telephone.route('/client/telephone/show')
def client_telephone_show():
    mycursor = get_db().cursor()

    query = '''SELECT telephone.id_telephone, telephone.libelle_telephone, telephone.image_telephone, prix_telephone,
            SUM(stock) AS stock, COUNT(id_declinaison_telephone) AS nb_declinaisons
            FROM declinaison
            JOIN telephone ON declinaison.telephone_id = telephone.id_telephone
            '''
    list_param = []
    condition_and = ""
    if "filter_word" in session or "filter_prix_min" in session or "filter_prix_max" in session or "filter_types" in session:
        query = query + " WHERE "
    if 'filter_word' in session:
        query = query + " libelle_telephone LIKE %s "
        recherche = "%" + session['filter_word'] + "%"
        list_param.append(recherche)
        condition_and = " AND "
    if 'filter_prix_min' in session or 'filter_prix_max' in session:
        query = query + condition_and + 'prix_telephone BETWEEN %s AND %s'
        list_param.append(session['filter_prix_min'])
        list_param.append(session['filter_prix_max'])
        condition_and = " AND "
    if 'filter_types' in session:
        query = query + condition_and + "("
        last_item = session['filter_types'][-1]
        for item in session['filter_types']:
            query = query + "modele_id=%s"
            if item != last_item:
                query = query + " OR "
            list_param.append(item)
        query = query + ")"
    query += "GROUP BY id_telephone"
    tuple_sql = tuple(list_param)
    mycursor.execute(query, tuple_sql)
    telephones = mycursor.fetchall()

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

    sql = '''SELECT telephone.libelle_telephone, telephone.prix_telephone, ligne_panier.quantite, telephone.id_telephone, declinaison.couleur_id, declinaison.taille_id, couleur.libelle_couleur, taille.libelle_taille
               FROM ligne_panier 
               JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison_telephone
               JOIN telephone ON ligne_panier.declinaison_id = telephone.id_telephone 
               JOIN couleur ON declinaison.couleur_id = couleur.id_couleur
               JOIN taille ON declinaison.taille_id = taille.id_taille
               WHERE ligne_panier.utilisateur_id = %s'''
    mycursor.execute(sql, (id_client,))
    telephones_panier = mycursor.fetchall()

    prix_total = sum(item['quantite'] * item['prix_telephone'] for item in telephones_panier)

    return render_template('client/boutique/panier_telephone.html',
                           telephones=telephones,
                           telephones_panier=telephones_panier,
                           items_filtre=modele,
                           prix_total=prix_total)
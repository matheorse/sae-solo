#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__, template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT *, prix_telephone FROM ligne_panier
             LEFT JOIN declinaison d ON ligne_panier.declinaison_id = d.id_declinaison_telephone
             LEFT JOIN telephone t ON d.telephone_id = t.id_telephone
             LEFT JOIN couleur c ON d.couleur_id = c.id_couleur
             LEFT JOIN taille t ON d.taille_id= t.id_taille
             WHERE utilisateur_id=%s'''
    mycursor.execute(sql, (id_client,))
    telephones_panier = mycursor.fetchall()

    prix_total = None
    if len(telephones_panier) >= 1:
        sql = '''SELECT SUM(prix_telephone*quantite) AS prix_commande FROM ligne_panier lp
                 LEFT JOIN declinaison d ON lp.declinaison_id = d.id_declinaison_telephone
                 LEFT JOIN telephone t ON d.telephone_id = t.id_telephone
                 WHERE utilisateur_id=%s'''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()['prix_commande']

    return render_template('client/boutique/panier_validation_adresses.html', telephones_panier=telephones_panier, prix_total=prix_total, validation=1)


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT *, t.prix_telephone FROM ligne_panier lp
             JOIN declinaison d ON lp.declinaison_id = d.id_declinaison_telephone
             JOIN telephone t ON d.telephone_id = t.id_telephone
             WHERE utilisateur_id=%s;'''
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()
    if items_ligne_panier is None or len(items_ligne_panier) < 1:
        flash(u'Pas d\'telephones dans le ligne_panier', 'alert-warning')
        return redirect('/client/telephone/show')

    sql = '''INSERT INTO commande(date_achat_commande, utilisateur_id, etat_id) VALUES (NOW(), %s, 1);'''
    mycursor.execute(sql, (id_client,))
    sql = '''SELECT last_insert_id() as last_insert_id'''
    mycursor.execute(sql)
    derniere_commande = mycursor.fetchone()['last_insert_id']
    for item in items_ligne_panier:
        id_declinaison_telephone = item['telephone_declinaison_id']
        prix_commande = item['prix_telephone']
        quantite_commande = item['quantite_panier']
        sql = '''DELETE FROM ligne_panier
                 WHERE declinaison_id = %s AND utilisateur_id = %s;'''
        mycursor.execute(sql, (id_declinaison_telephone, id_client,))
        sql = '''INSERT INTO ligne_commande(commande_id, declinaison_id, prix, quantite) VALUES(%s, %s, %s, %s);'''
        mycursor.execute(sql, (derniere_commande, id_declinaison_telephone, prix_commande, quantite_commande,))
    get_db().commit()
    flash(u'Commande ajoutée', 'alert-success')
    return redirect('/client/telephone/show')


@client_commande.route('/client/commande/show', methods=['get', 'post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql_commandes = '''SELECT id_commande, etat_id, date_achat_commande, 
                              SUM(ligne_commande.quantite) AS nbr_declinaisons, 
                              SUM(ligne_commande.prix * ligne_commande.quantite) AS prix_total, 
                              etat.libelle_etat
                       FROM commande
                       JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
                       JOIN etat ON commande.etat_id = etat.id_etat
                       WHERE utilisateur_id = %s
                       GROUP BY id_commande, etat_id, date_achat_commande, etat.libelle_etat   
                       ORDER BY etat_id, date_achat_commande DESC;'''
    mycursor.execute(sql_commandes, (id_client,))
    commandes = mycursor.fetchall()

    telephones_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande:
        sql_telephones = '''SELECT t.libelle_telephone AS nom, lc.quantite, 
                                   lc.prix AS prix_unitaire, 
                                   (lc.prix * lc.quantite) AS prix_total,
                                   c.libelle_couleur, ta.libelle_taille,
                                   (SELECT COUNT(*) FROM declinaison d2 WHERE d2.telephone_id = t.id_telephone) AS nb_declinaisons
                            FROM ligne_commande lc
                            JOIN declinaison d ON lc.declinaison_id = d.id_declinaison_telephone
                            JOIN telephone t ON d.telephone_id = t.id_telephone
                            JOIN couleur c ON d.couleur_id = c.id_couleur
                            JOIN taille ta ON d.taille_id = ta.id_taille
                            WHERE lc.commande_id = %s;'''
        mycursor.execute(sql_telephones, (id_commande,))
        telephones_commande = mycursor.fetchall()

    return render_template('client/commandes/show.html', commandes=commandes, telephones_commande=telephones_commande, commande_adresses=commande_adresses)
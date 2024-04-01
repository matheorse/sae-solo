#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                           template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    #admin_id = session['id_user']
    sql = '''SELECT
    u.login AS 'Login Client',
    c.date_achat_commande AS 'Date de Commande',
    SUM(lc.quantite) AS 'Nombre de telephone',
    SUM(lc.prix * lc.quantite) AS 'Cout Total',
    e.libelle_etat AS 'Etat de la Commande',
    c.id_commande AS 'ID Commande'
FROM
    commande c
JOIN
    utilisateur u ON c.utilisateur_id = u.id_utilisateur
JOIN
    etat e ON c.etat_id = e.id_etat
LEFT JOIN
    ligne_commande lc ON c.id_commande = lc.commande_id
GROUP BY
    c.id_commande
ORDER BY
    e.libelle_etat, c.date_achat_commande DESC
'''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()



    telephones_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    print(id_commande)
    if id_commande is not None:
        sql = '''SELECT c.id_commande,
                       t.libelle_telephone,
                       lc.quantite,
                       lc.prix AS prix_unitaire,
                       (lc.quantite * lc.prix) AS prix_total,
                       c.etat_id,
                       u.nom,
                       a.nom_adresse AS adresse_livraison_nom,
                       a.rue_adresse AS adresse_livraison_rue,
                       a.code_postal AS adresse_livraison_cp,
                       a.ville AS adresse_livraison_ville,
                       a2.nom_adresse AS adresse_facturation_nom,
                       a2.rue_adresse AS adresse_facturation_rue,
                       a2.code_postal AS adresse_facturation_cp,
                       a2.ville AS adresse_facturation_ville,
                       c.date_achat_commande,
                       co.libelle_couleur,
                       ta.libelle_taille
                FROM commande c
                JOIN ligne_commande lc ON c.id_commande = lc.commande_id
                JOIN declinaison_telephone dt ON lc.declinaison_id = dt.id_declinaison
                JOIN telephone t ON dt.id_telephone = t.id_telephone
                JOIN couleur co ON dt.id_couleur = co.id_couleur
                JOIN taille ta ON dt.id_taille = ta.id_taille
                JOIN adresse a ON c.adresse_id = a.id_adresse
                JOIN adresse a2 ON c.adresse_1_id = a2.id_adresse
                JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
                WHERE c.id_commande = %s'''

        mycursor.execute(sql, (id_commande,))
        telephones_commande = mycursor.fetchall()

        if telephones_commande:
            commande_adresses = {
                'nom': telephones_commande[0]['nom'],
                'adresse_livraison_nom': telephones_commande[0]['adresse_livraison_nom'],
                'adresse_livraison_rue': telephones_commande[0]['adresse_livraison_rue'],
                'adresse_livraison_cp': telephones_commande[0]['adresse_livraison_cp'],
                'adresse_livraison_ville': telephones_commande[0]['adresse_livraison_ville'],
                'adresse_facturation_nom': telephones_commande[0]['adresse_facturation_nom'],
                'adresse_facturation_rue': telephones_commande[0]['adresse_facturation_rue'],
                'adresse_facturation_cp': telephones_commande[0]['adresse_facturation_cp'],
                'adresse_facturation_ville': telephones_commande[0]['adresse_facturation_ville'],
                'date_achat_commande': telephones_commande[0]['date_achat_commande']
            }
        else:
            commande_adresses = {}

    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , telephones_commande=telephones_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)

    if commande_id != None :
        print(commande_id)

        sql = 'UPDATE commande SET etat_id = 2 WHERE id_commande = %s'
        mycursor.execute(sql, (commande_id,))
        get_db().commit()

    return redirect('/admin/commande/show')




#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__,
                              template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()

    # Récupère l'ID de l'utilisateur courant à partir de la session
    id_client = session['id_user']

    # Requête pour récupérer les informations de l'utilisateur
    sql_utilisateur = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()  # Utilise fetchone() si on attend un seul résultat

    # Requête pour récupérer toutes les adresses de l'utilisateur
    sql_adresses = """
    SELECT adresse.*, 
           COUNT(DISTINCT commande.id_commande) AS nb_commandes
    FROM adresse
    LEFT JOIN commande ON adresse.id_adresse = commande.adresse_id OR adresse.id_adresse = commande.adresse_1_id
    WHERE adresse.id_utilisateur = %s
    GROUP BY adresse.id_adresse
    """
    mycursor.execute(sql_adresses, (id_client,))
    adresses = mycursor.fetchall()  # Utilise fetchall() pour récupérer tous les résultats

    # Calcul du nombre d'adresses
    nb_adresses = sum(1 for adresse in adresses if adresse['valide'] is None or adresse['valide'] != 0)


    # Retourne le template avec les informations de l'utilisateur et ses adresses
    return render_template('client/coordonnee/show_coordonnee.html',
                           utilisateur=utilisateur,
                           adresses=adresses,
                           nb_adresses=nb_adresses)


@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Requête pour récupérer les informations de l'utilisateur
    sql_utilisateur = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()  # Utilise fetchone() si on attend un seul résultat

    # Retourne le template avec les informations de l'utilisateur pré-remplies pour édition
    return render_template('client/coordonnee/edit_coordonnee.html',
                           utilisateur=utilisateur)


@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    # Vérifier si l'email ou le login existe déjà pour un autre utilisateur
    sql_verification = """SELECT id_utilisateur FROM utilisateur WHERE (email = %s OR login = %s) AND id_utilisateur != %s"""
    mycursor.execute(sql_verification, (email, login, id_client))
    utilisateur_existant = mycursor.fetchone()

    if utilisateur_existant:
        # Si l'utilisateur existe déjà, informer l'utilisateur courant
        flash(u'Cet email ou ce login existe déjà pour un autre utilisateur.', 'alert-warning')
        return render_template('client/coordonnee/edit_coordonnee.html', utilisateur={'nom': nom, 'login': login, 'email': email, 'id_utilisateur': id_client})
    else:
        # Mettre à jour les informations de l'utilisateur
        sql_update = """UPDATE utilisateur SET nom = %s, login = %s, email = %s WHERE id_utilisateur = %s"""
        mycursor.execute(sql_update, (nom, login, email, id_client))
        get_db().commit()

        # Informer l'utilisateur du succès de la mise à jour
        flash(u'Vos informations ont été mises à jour avec succès.', 'alert-success')
        return redirect('/client/coordonnee/show')



@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')

    # Vérifier si l'adresse est liée à une commande
    sql_verification = """SELECT id_commande FROM commande WHERE adresse_id = %s OR adresse_1_id = %s"""
    mycursor.execute(sql_verification, (id_adresse, id_adresse,))
    commande_associee = mycursor.fetchone()

    if commande_associee:
        # Si l'adresse est liée à une commande, la rendre invalide au lieu de la supprimer
        sql_invalide = """UPDATE adresse SET valide = 0 WHERE id_adresse = %s"""
        mycursor.execute(sql_invalide, (id_adresse,))
    else:
        # Si l'adresse n'est pas liée à une commande, la supprimer de la base de données
        sql_delete = """DELETE FROM adresse WHERE id_adresse = %s"""
        mycursor.execute(sql_delete, (id_adresse,))

    # Marquer toutes les adresses de cet utilisateur comme non favorites
    sql_reset_favori = """UPDATE adresse SET favori = 0 WHERE id_utilisateur = %s"""
    mycursor.execute(sql_reset_favori, (id_client,))

    # Trouver et rendre favori l'adresse avec le plus grand nombre de commandes
    sql_new_favori = """
    UPDATE adresse
    SET favori = 1
    WHERE id_adresse = (
        SELECT id_adresse FROM (
            SELECT a.id_adresse
            FROM adresse a
            LEFT JOIN commande c ON a.id_adresse = c.adresse_id OR a.id_adresse = c.adresse_1_id
            WHERE a.id_utilisateur = %s AND a.valide = 1
            GROUP BY a.id_adresse
            ORDER BY COUNT(c.id_commande) DESC, a.date_utilisation DESC
            LIMIT 1
        ) AS subquery
    ) AND id_utilisateur = %s
    """
    mycursor.execute(sql_new_favori, (id_client, id_client))

    get_db().commit()

    if commande_associee:
        flash(u"Cette adresse est liée à une commande et ne peut pas être supprimée. Elle a été marquée comme invalide.", 'alert-warning')
    else:
        flash(u"L'adresse a été supprimée avec succès.", 'alert-success')

    return redirect('/client/coordonnee/show')






@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Requête pour récupérer les informations de l'utilisateur
    sql_utilisateur = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html', utilisateur=utilisateur)


@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    # Requête pour insérer la nouvelle adresse dans la base de données
    sql_insert_adresse = "INSERT INTO adresse (nom_adresse, rue_adresse, code_postal, ville,favori,valide, date_utilisation, id_utilisateur) VALUES (%s,%s,%s, %s, %s, %s, CURDATE(), %s)"
    mycursor.execute(sql_insert_adresse, (nom, rue, code_postal, ville, 0, 1, id_client))
    get_db().commit()

    flash(u'Votre nouvelle adresse a été ajoutée avec succès.', 'alert-success')
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')

    # Requête pour récupérer les informations de l'utilisateur concerné
    sql_select_utilisateur = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql_select_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()

    # Requête pour récupérer les informations de l'adresse à éditer
    sql_select_adresse = "SELECT * FROM adresse WHERE id_adresse = %s"
    mycursor.execute(sql_select_adresse, (id_adresse,))
    adresse = mycursor.fetchone()

    return render_template('/client/coordonnee/edit_adresse.html', utilisateur=utilisateur, adresse=adresse)


@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    # Vérifier si l'adresse est favorite
    sql_check_favori = "SELECT favori FROM adresse WHERE id_adresse = %s AND id_utilisateur = %s"
    mycursor.execute(sql_check_favori, (id_adresse, id_client))
    result = mycursor.fetchone()
    est_favori = result['favori'] if result else None

    # Vérifier si l'adresse a été utilisée pour une commande
    sql_check_commande = "SELECT id_commande FROM commande WHERE adresse_id = %s OR adresse_1_id = %s"
    mycursor.execute(sql_check_commande, (id_adresse, id_adresse))
    commande = mycursor.fetchone()

    if commande:
        # Marquer l'adresse actuelle comme non valide
        sql_invalider_adresse = "UPDATE adresse SET valide = 0 WHERE id_adresse = %s"
        mycursor.execute(sql_invalider_adresse, (id_adresse,))

        # Créer un doublon de l'adresse avec les nouvelles informations et la rendre favori si nécessaire
        favori_status = 1 if est_favori else 0
        sql_insert_adresse = "INSERT INTO adresse (nom_adresse, rue_adresse, code_postal, ville, id_utilisateur, favori, valide) VALUES (%s, %s, %s, %s, %s, %s, 1)"
        mycursor.execute(sql_insert_adresse, (nom, rue, code_postal, ville, id_client, favori_status))
    else:
        # Si l'adresse n'a pas été utilisée pour une commande, mettre à jour directement
        sql_update_adresse = "UPDATE adresse SET nom_adresse = %s, rue_adresse = %s, code_postal = %s, ville = %s WHERE id_adresse = %s AND id_utilisateur = %s"
        mycursor.execute(sql_update_adresse, (nom, rue, code_postal, ville, id_adresse, id_client))

    get_db().commit()

    flash(u'Votre adresse a été mise à jour avec succès.', 'alert-success')
    return redirect('/client/coordonnee/show')




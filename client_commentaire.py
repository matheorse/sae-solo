#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime

from connexion_db import get_db

from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__,
                        template_folder='templates')

@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()

    commentaire = request.form.get('commentaire', None)
    id_client = session.get('id_user')
    id_telephone = request.form.get('id_telephone', None)
    date_publication = datetime.now().strftime('%Y-%m-%d')

    print("ID client:", id_client)
    print("ID téléphone:", id_telephone)

    if not commentaire or len(commentaire) < 3:
        flash('Le commentaire doit contenir au moins 3 caractères.', 'error')
        return redirect(url_for('client_telephone.telephone_details', id_telephone=id_telephone))

    # Vérifier si l'utilisateur a déjà 3 commentaires pour cet article
    sql_count_comments = """
    SELECT COUNT(*) 
    FROM commentaire 
    WHERE utilisateur_id = %s AND telephone_id = %s
    """
    mycursor.execute(sql_count_comments, (id_client, id_telephone))
    existing_comments_row = mycursor.fetchone()

    print("Nombre de commentaires existants:", existing_comments_row)

    if existing_comments_row:
        existing_comments = existing_comments_row['COUNT(*)']
    else:
        existing_comments = 0

    print("Nombre de commentaires existants (valeur réelle):", existing_comments)

    if existing_comments < 3:
        sql_ajout_commentaire = """
            INSERT INTO commentaire (id_commentaire, telephone_id, utilisateur_id, date_publication, commentaire, valider)
            VALUES (NULL, %s, %s, %s, %s, TRUE)
            """
        mycursor.execute(sql_ajout_commentaire, (id_telephone, id_client, date_publication, commentaire))
        get_db().commit()
        flash('Votre commentaire a été ajouté avec succès.', 'success')
    elif existing_comments >= 3:
        flash("Vous ne pouvez pas poster plus de trois commentaires", 'error')
    else:
        flash("Vous ne pouvez pas commenter sur cet article sans l'avoir acheté.", 'error')

    return redirect(url_for('client_telephone.telephone_details', id_telephone=id_telephone))


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_delete():
    print(request.form)
    # Récupération de l'ID du téléphone et de la date de publication à partir du formulaire
    id_telephone = request.form.get('id_telephone')
    date_publication = request.form.get('date_publication')
    id_client = session['id_user']


    # SQL pour supprimer le commentaire
    sql = """
    DELETE FROM commentaire 
    WHERE utilisateur_id = %s AND telephone_id = %s AND date_publication = %s
    """
    mycursor = get_db().cursor()
    mycursor.execute(sql, (id_client, id_telephone, date_publication))
    get_db().commit()

    # Redirection vers la page des détails du téléphone avec l'ID du téléphone
    return redirect(url_for('client_telephone.telephone_details', id_telephone=id_telephone))

@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    id_client = session.get('id_user')  # Assurez-vous que 'id_user' est bien la clé utilisée dans la session
    id_telephone = request.form.get('id_telephone')
    note = request.form.get('note')

    # Convertir la note en float pour validation
    try:
        note = float(note)
        if not (0 <= note <= 5):
            raise ValueError("La note doit être entre 0 et 5.")
    except ValueError as e:
        flash(f"Erreur: {e}", 'error')
        return redirect(url_for('client_telephone.telephone_details', id_telephone=id_telephone))

    # Connexion à la base de données et insertion/mise à jour de la note
    mycursor = get_db().cursor()

    # Requête SQL pour insérer ou mettre à jour la note
    sql = """
    INSERT INTO note (telephone_id, utilisateur_id, note)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE note = VALUES(note)
    """

    try:
        mycursor.execute(sql, (id_telephone, id_client, note))
        get_db().commit()
        flash('Votre note a été mise à jour.', 'success')
    except Exception as e:
        flash(f"Erreur lors de la mise à jour de la note: {e}", 'error')

    return redirect(url_for('client_telephone.telephone_details', id_telephone=id_telephone))


@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_update = (note, id_client, id_article)
    print(tuple_update)
    sql = '''  '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    tuple_delete = (id_client, id_article)
    print(tuple_delete)
    sql = '''  '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                        template_folder='templates')


@admin_commentaire.route('/admin/telephone/commentaires', methods=['GET'])
def admin_telephone_details():
    mycursor = get_db().cursor()
    id_telephone = request.args.get('id_telephone', None)

    # Récupérer les informations sur le téléphone
    sql = '''
        SELECT * FROM telephone WHERE id_telephone = %s
    '''
    mycursor.execute(sql, (id_telephone,))
    telephone = mycursor.fetchone()

    # Récupérer les commentaires associés au téléphone
    sql = '''
        SELECT * FROM commentaire WHERE id_telephone = %s ORDER BY date_publication DESC
    '''
    mycursor.execute(sql, (id_telephone,))
    commentaires = mycursor.fetchall()

    return render_template('admin/telephone/show_telephone_commentaires.html'
                           , commentaires=commentaires
                           , telephone=telephone
                           )

@admin_commentaire.route('/admin/telephone/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_utilisateur = request.form.get('id_utilisateur', None)
    id_telephone = request.form.get('id_telephone', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''    requête admin_type_telephone_2   '''
    tuple_delete=(id_utilisateur,id_telephone,date_publication)
    get_db().commit()
    return redirect('/admin/telephone/commentaires?id_telephone='+id_telephone)


@admin_commentaire.route('/admin/telephone/commentaires/repondre', methods=['POST','GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_utilisateur = request.args.get('id_utilisateur', None)
        id_telephone = request.args.get('id_telephone', None)
        date_publication = request.args.get('date_publication', None)
        return render_template('admin/telephone/add_commentaire.html',id_utilisateur=id_utilisateur,id_telephone=id_telephone,date_publication=date_publication )

    mycursor = get_db().cursor()
    id_utilisateur = session['id_user']   #1 admin
    id_telephone = request.form.get('id_telephone', None)
    date_publication = request.form.get('date_publication', None)
    commentaire = request.form.get('commentaire', None)
    sql = '''    requête admin_type_telephone_3   '''
    get_db().commit()
    return redirect('/admin/telephone/commentaires?id_telephone='+id_telephone)


@admin_commentaire.route('/admin/telephone/commentaires/valider', methods=['POST','GET'])
def admin_comment_valider():
    id_telephone = request.args.get('id_telephone', None)
    mycursor = get_db().cursor()
    sql = '''   requête admin_type_telephone_4   '''
    get_db().commit()
    return redirect('/admin/telephone/commentaires?id_telephone='+id_telephone)
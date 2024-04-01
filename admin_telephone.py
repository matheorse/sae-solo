#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_telephone = Blueprint('admin_telephone', __name__,
                            template_folder='templates')




from flask import render_template

@admin_telephone.route('/admin/telephone/show')
def show_telephone():
    mycursor = get_db().cursor()
    sql = '''SELECT t.id_telephone, t.libelle_telephone, t.prix_telephone, t.image_telephone, t.modele_id, m.libelle_modele, SUM(stock) AS stock, MIN(stock) AS min_stock
                 FROM telephone t
                 LEFT JOIN declinaison d ON t.id_telephone = d.telephone_id
                 LEFT JOIN modele m ON t.modele_id = m.id_modele
                 GROUP BY id_telephone'''
    mycursor.execute(sql)
    telephones = mycursor.fetchall()

    return render_template('admin/telephone/show_telephone.html', telephones=telephones)


@admin_telephone.route('/admin/telephone/add', methods=['GET'])
def add_telephone():

    mycursor = get_db().cursor()


    sql = ''' SELECT * FROM modele'''
    mycursor.execute(sql)
    modeles = mycursor.fetchall()

    sql = ''' SELECT * FROM couleur'''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()

    return render_template('admin/telephone/add_telephone.html', modeles=modeles, couleurs=couleurs)


@admin_telephone.route('/admin/telephone/add', methods=['POST'])
def valid_add_telephone():
    mycursor = get_db().cursor()

    libelle_telephone = request.form.get('libelle', '')
    stock = request.form.get('stock', '')
    poids = request.form.get('poids', '')
    taille = request.form.get('taille', '')
    stockage = request.form.get('stockage', '')
    prix = request.form.get('prix', '')
    autonomie = request.form.get('autonomie', '')
    image = request.files.get('image')
    modele_id = request.form.get('modele_id', '')
    couleur_id = request.form.get('couleur_id', '')


    if image:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join('static/images/', image_filename))
    else:
        image_filename = ''


    sql = '''INSERT INTO telephone (libelle_telephone, poids_telephone, stockage_telephone, prix_telephone, autonomie_telephone, image_telephone, modele_id)
             VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    mycursor.execute(sql, (libelle_telephone, poids, stockage, prix, autonomie, image_filename, modele_id))
    id_telephone = mycursor.lastrowid


    sql_couleur = '''INSERT INTO declinaison (telephone_id, couleur_id, taille_id, stock, prix_declinaison)
                     VALUES (%s, %s, %s, %s, %s)'''
    mycursor.execute(sql_couleur, (id_telephone, couleur_id, 1, stock, prix))

    get_db().commit()


    telephone_info = {
        'Libellé': libelle_telephone,
        'Stock': stock,
        'Poids': poids + ' g',
        'Taille': taille + ' pouces',
        'Stockage': stockage + ' Go',
        'Prix': prix + ' €',
        'Autonomie': autonomie + ' heures',
        'Image': image_filename,
        'Modèle': modele_id,
        'Couleur': couleur_id
    }

    message = 'Téléphone ajouté avec succès - Informations:\n'
    for key, value in telephone_info.items():
        message += f'{key}: {value} | '

    flash(message.rstrip('| '), 'alert-success')
    return redirect('/admin/telephone/show')



@admin_telephone.route('/admin/telephone/delete', methods=['GET'])
def delete_telephone():
    id_telephone = request.args.get('id_telephone')
    mycursor = get_db().cursor()

    sql_count_couleurs = '''SELECT COUNT(*) as nb_couleurs FROM declinaison WHERE couleur_id = %s'''
    mycursor.execute(sql_count_couleurs, (id_telephone,))
    nb_couleurs = mycursor.fetchone()

    if nb_couleurs['nb_couleurs'] > 0:
        message = u"Il y a des couleurs associées à ce téléphone : vous ne pouvez pas le supprimer"
        flash(message, 'alert-warning')
    else:
        sql_get_image = '''SELECT image_telephone FROM telephone WHERE id_telephone = %s'''
        mycursor.execute(sql_get_image, (id_telephone,))
        telephone = mycursor.fetchone()
        image = telephone['image_telephone']

        sql_delete_telephone = '''DELETE FROM telephone WHERE id_telephone = %s'''
        mycursor.execute(sql_delete_telephone, (id_telephone,))
        get_db().commit()

        if image is not None:
            os.remove('static/images/' + image)

        print("Un téléphone supprimé, id :", id_telephone)
        message = u"Un téléphone a été supprimé, ID : " + id_telephone
        flash(message, 'alert-success')

    return redirect('/admin/telephone/show')

@admin_telephone.route('/admin/telephone/edit', methods=['GET'])
def edit_telephone():
    id_telephone = request.args.get('id_telephone')
    mycursor = get_db().cursor()
    sql = '''
    SELECT * FROM telephone WHERE id_telephone = %s
    '''
    mycursor.execute(sql, (id_telephone,))
    telephone = mycursor.fetchone()

    sql_modeles = '''
    SELECT id_modele, libelle_modele FROM modele
    '''
    mycursor.execute(sql_modeles)
    modeles = mycursor.fetchall()

    sql_declinaisons = '''
    SELECT d.couleur_id, d.taille_id, d.stock, c.libelle_couleur, t.libelle_taille
    FROM declinaison d
    LEFT JOIN couleur c ON c.id_couleur = d.couleur_id
    LEFT JOIN taille t ON t.id_taille = d.taille_id
    WHERE d.telephone_id = %s
    '''
    mycursor.execute(sql_declinaisons, (id_telephone,))
    declinaisons = mycursor.fetchall()

    sql_count_couleurs = '''SELECT COUNT(*) as nb_couleurs FROM declinaison WHERE telephone_id = %s'''
    mycursor.execute(sql_count_couleurs, (id_telephone,))
    nb_couleurs = mycursor.fetchone()

    nb_couleurs_int = int(nb_couleurs['nb_couleurs'])

    return render_template('admin/telephone/edit_telephone.html',
                           telephone=telephone,
                           modeles=modeles,
                           declinaisons=declinaisons,
                           nb_couleurs=nb_couleurs_int
                           )



@admin_telephone.route('/admin/telephone/edit', methods=['POST'])
def valid_edit_telephone():
    mycursor = get_db().cursor()
    id_telephone = request.form.get('id_telephone')
    nom = request.form.get('nom')
    stock = request.form.get('stock')
    poids = request.form.get('poids')
    taille = request.form.get('taille')
    stockage = request.form.get('stockage')
    prix = request.form.get('prix')
    autonomie = request.form.get('autonomie')
    image = request.files.get('image', '')
    modele_id = request.form.get('modele_id')

    sql_get_image = '''
    SELECT image_telephone FROM telephone WHERE id_telephone = %s
    '''
    mycursor.execute(sql_get_image, (id_telephone,))
    current_image = mycursor.fetchone()['image_telephone']

    if image:
        if current_image and os.path.exists(os.path.join(os.getcwd() + "/static/images/", current_image)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", current_image))
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        filename = current_image

    sql_update_telephone = '''
    UPDATE telephone
    SET libelle_telephone = %s,  poids_telephone = %s,
    stockage_telephone = %s, prix_telephone = %s, autonomie_telephone = %s, image_telephone = %s, modele_id = %s
    WHERE id_telephone = %s
    '''
    mycursor.execute(sql_update_telephone, (
        nom, stock, poids, taille, stockage, prix, autonomie, filename, modele_id, id_telephone))
    get_db().commit()

    telephone_info = {
        'Nom': nom,
        'Stock': stock,
        'Poids': poids + ' g',
        'Taille': taille + ' pouces',
        'Stockage': stockage + ' Go',
        'Prix': prix + ' €',
        'Autonomie': autonomie + ' heures',
        'Image': filename,
        'Modèle': modele_id,
    }

    message = 'Téléphone modifié avec succès - Informations:\n'
    for key, value in telephone_info.items():
        message += f'{key}: {value} | '

    flash(message, 'alert-success')

    return redirect('/admin/telephone/show')




@admin_telephone.route('/admin/telephone/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    telephone=[]
    commentaires = {}
    return render_template('admin/telephone/show_avis.html'
                           , telephone=telephone
                           , commentaires=commentaires
                           )


@admin_telephone.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    telephone_id = request.form.get('idtelephone', None)
    userId = request.form.get('idUser', None)

    return admin_avis(telephone_id)

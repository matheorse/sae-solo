#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_telephone = Blueprint('admin_declinaison_telephone', __name__,
                         template_folder='templates')


@admin_declinaison_telephone.route('/admin/declinaison_telephone/add')
def add_declinaison_telephone():
    mycursor = get_db().cursor()
    id_telephone = request.args.get('id_telephone')
    sql = '''SELECT * FROM telephone
             WHERE id_telephone = %s;'''
    mycursor.execute(sql, (id_telephone, ))
    telephone = mycursor.fetchone()
    sql = '''SELECT id_couleur, libelle_couleur FROM couleur'''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()
    sql = '''SELECT id_taille, libelle_taille FROM taille'''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()
    sql = '''SELECT id_taille FROM taille;'''
    mycursor.execute(sql)
    d_taille_uniq = mycursor.fetchone()
    sql = '''SELECT id_couleur FROM couleur;'''
    mycursor.execute(sql)
    d_couleur_uniq = mycursor.fetchone()
    return render_template('admin/telephone/add_declinaison.html', telephone = telephone, couleurs=couleurs, tailles=tailles, d_taille_uniq=d_taille_uniq, d_couleur_uniq=d_couleur_uniq)


@admin_declinaison_telephone.route('/admin/declinaison_telephone/add', methods=['POST'])
def valid_add_declinaison_telephone():
    mycursor = get_db().cursor()
    stock_declinaison = request.form.get('stock')
    id_telephone = request.form.get('id_telephone')
    taille_id = request.form.get('taille_id', None)
    couleur_id = request.form.get('couleur_id', None)

    # Vérifiez l'existence de la déclinaison
    sql = '''SELECT stock FROM declinaison
             WHERE telephone_id = %s AND taille_id = %s AND couleur_id = %s'''
    mycursor.execute(sql, (id_telephone, taille_id, couleur_id))
    declinaison_present = mycursor.fetchone()

    if declinaison_present:
        # Mise à jour du stock existant
        nouveau_stock = declinaison_present[0] + int(stock_declinaison)
        sql_update = '''UPDATE declinaison SET stock = %s
                        WHERE telephone_id = %s AND taille_id = %s AND couleur_id = %s'''
        mycursor.execute(sql_update, (nouveau_stock, id_telephone, taille_id, couleur_id))
        flash('Doublon sur cette déclinaison, seul le stock a été mis à jour', 'alert-warning')
    else:
        # Insertion d'une nouvelle déclinaison
        sql_insert = '''INSERT INTO declinaison (stock, telephone_id, taille_id, couleur_id) VALUES (%s, %s, %s, %s)'''
        mycursor.execute(sql_insert, (stock_declinaison, id_telephone, taille_id, couleur_id))
        message = 'Déclinaison ajoutée, id téléphone: ' + str(id_telephone) + ', stock: ' + str(stock_declinaison) + ', taille: ' + str(taille_id) + ', couleur: ' + str(couleur_id)
        flash(message, 'alert-success')

    get_db().commit()
    return redirect('/admin/telephone/edit?id_telephone=' + id_telephone)  # Corrigé de /admin/velo/edit?id_velo= à /admin/telephone/edit?id_telephone=


@admin_declinaison_telephone.route('/admin/declinaison_telephone/edit', methods=['GET'])
def edit_declinaison_telephone():
    id_declinaison_telephone = request.args.get('id_declinaison_telephone')
    mycursor = get_db().cursor()
    declinaison_telephone=[]
    declinaisons=None
    tailles=None
    d_taille_uniq=None
    d_declinaison_uniq=None
    return render_template('admin/telephone/edit_declinaison.html'
                           , tailles=tailles
                           , declinaisons=declinaisons
                           , declinaison_telephone=declinaison_telephone
                           , d_taille_uniq=d_taille_uniq
                           , d_declinaison_uniq=d_declinaison_uniq
                           )


@admin_declinaison_telephone.route('/admin/declinaison_telephone/edit', methods=['POST'])
def valid_edit_declinaison_telephone():
    id_declinaison_telephone = request.form.get('id_declinaison_telephone','')
    id_telephone = request.form.get('id_telephone','')
    stock = request.form.get('stock','')
    taille_id = request.form.get('id_taille','')
    declinaison_id = request.form.get('id_declinaison','')
    mycursor = get_db().cursor()

    message = u'declinaison_telephone modifié , id:' + str(id_declinaison_telephone) + '- stock :' + str(stock) + ' - taille_id:' + str(taille_id) + ' - declinaison_id:' + str(declinaison_id)
    flash(message, 'alert-success')
    return redirect('/admin/telephone/edit?id_telephone=' + str(id_telephone))


@admin_declinaison_telephone.route('/admin/declinaison_telephone/delete', methods=['GET'])
def admin_delete_declinaison_telephone():
    mycursor = get_db().cursor()
    id_declinaison_telephone = request.args.get('id_declinaison_telephone', '')
    id_telephone = request.args.get('id_telephone', '')
    sql = '''SELECT * FROM ligne_panier 
             WHERE declinaison_id = %s'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    declinaisons_dans_panier = mycursor.fetchall()

    sql = '''SELECT * FROM ligne_commande
             WHERE declinaison_id = %s'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    declinaisons_dans_commande = mycursor.fetchall()

    if declinaisons_dans_panier:
        flash('Il y a des exemplaires dans des paniers : vous ne pouvez pas le supprimer', 'alert-warning')
    elif declinaisons_dans_commande:
        flash('Il y a des exemplaires dans des commandes : vous ne pouvez pas le supprimer', 'alert-warning')
    else:
        sql = '''DELETE FROM declinaison
                 WHERE id_declinaison_telephone = %s AND telephone_id = %s'''
        mycursor.execute(sql, (id_declinaison_telephone, id_telephone,))
        get_db().commit()
        flash(u'Déclinaison supprimée avec succès, id_declinaison_telephone : ' + str(id_declinaison_telephone), 'alert-success')

    return redirect('/admin/telephone/edit?id_telephone=' + str(id_telephone))

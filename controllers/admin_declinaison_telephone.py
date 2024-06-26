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
    mycursor.execute(sql, (id_telephone,))
    telephone = mycursor.fetchone()
    sql = '''SELECT id_couleur, libelle_couleur FROM couleur'''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()
    sql = '''SELECT id_taille, libelle_taille FROM taille'''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()
    sql = '''SELECT taille_id, id_declinaison_telephone FROM declinaison
                WHERE telephone_id = %s'''
    mycursor.execute(sql, (id_telephone,))
    d_taille_uniq = mycursor.fetchone()
    if d_taille_uniq is not None:
        tailles = tailles[1:]
        taille_id = d_taille_uniq.get('taille_id')
        if taille_id == 1:
            d_taille_uniq = 1
    sql = '''SELECT couleur_id, id_declinaison_telephone FROM declinaison
                     WHERE telephone_id = %s'''
    mycursor.execute(sql, (id_telephone,))
    d_couleur_uniq = mycursor.fetchone()
    if d_couleur_uniq is not None:
        couleurs = couleurs[1:]
        couleur_id = d_couleur_uniq.get('couleur_id')
        if couleur_id == 1:
            d_couleur_uniq = 1
    return render_template('admin/telephone/add_declinaison.html', telephone=telephone, couleurs=couleurs, tailles=tailles, d_taille_uniq=d_taille_uniq, d_couleur_uniq=d_couleur_uniq)

@admin_declinaison_telephone.route('/admin/declinaison_telephone/add', methods=['POST'])
def valid_add_declinaison_telephone():
    mycursor = get_db().cursor()
    stock_declinaison = request.form.get('stock')
    id_telephone = request.form.get('id_telephone')
    taille_id = request.form.get('taille_id', None)
    couleur_id = request.form.get('couleur_id', None)

    sql = '''SELECT * FROM declinaison
                 WHERE telephone_id = %s AND taille_id = %s AND couleur_id = %s'''
    mycursor.execute(sql, (id_telephone, taille_id, couleur_id))
    declinaison_present = mycursor.fetchall()

    if len(declinaison_present) > 0:
        sql_update = '''UPDATE declinaison SET stock = %s
                            WHERE telephone_id = %s AND taille_id = %s AND couleur_id = %s'''
        mycursor.execute(sql_update, (stock_declinaison, id_telephone, taille_id, couleur_id))
        flash('Doublon sur cette déclinaison, seul le stock a été mis à jour', 'alert-warning')
    else:
        sql_insert = '''INSERT INTO declinaison (stock, telephone_id, taille_id, couleur_id) VALUES (%s, %s, %s, %s)'''
        mycursor.execute(sql_insert, (stock_declinaison, id_telephone, taille_id, couleur_id))
        message = 'Déclinaison ajoutée, id téléphone: ' + str(id_telephone) + ', stock: ' + str(
            stock_declinaison) + ', taille: ' + str(taille_id) + ', couleur: ' + str(couleur_id)
        flash(message, 'alert-success')

    get_db().commit()
    return redirect('/admin/telephone/edit?id_telephone=' + id_telephone)


@admin_declinaison_telephone.route('/admin/declinaison_telephone/edit', methods=['GET'])
def edit_declinaison_telephone():
    mycursor = get_db().cursor()
    id_declinaison_telephone = request.args.get('id_declinaison_telephone')
    sql = '''SELECT * FROM declinaison
             JOIN telephone ON declinaison.telephone_id = telephone.id_telephone
             WHERE id_declinaison_telephone = %s;'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    declinaison_telephone = mycursor.fetchone()
    sql = '''SELECT id_couleur, libelle_couleur FROM couleur'''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()
    sql = '''SELECT id_taille, libelle_taille FROM taille'''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()
    sql = '''SELECT taille_id, id_declinaison_telephone FROM declinaison
             WHERE id_declinaison_telephone = %s'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    d_taille_uniq = mycursor.fetchone()
    if d_taille_uniq is not None:
        tailles = tailles[1:]
        taille_id = d_taille_uniq.get('taille_id')
        if taille_id == 1:
            d_taille_uniq = 1
    sql = '''SELECT couleur_id, id_declinaison_telephone FROM declinaison
                     WHERE id_declinaison_telephone = %s'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    d_couleur_uniq = mycursor.fetchone()
    if d_couleur_uniq is not None:
        couleurs = couleurs[1:]
        couleur_id = d_couleur_uniq.get('couleur_id')
        if couleur_id == 1:
            d_couleur_uniq = 1
    return render_template('admin/telephone/edit_declinaison.html'
                           , tailles=tailles
                           , couleurs=couleurs
                           , declinaison_telephone=declinaison_telephone
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_telephone.route('/admin/declinaison_telephone/edit', methods=['POST'])
def valid_edit_declinaison_telephone():
    id_declinaison_telephone = request.form.get('id_declinaison_telephone','')
    id_telephone = request.form.get('id_telephone','')
    stock = request.form.get('stock','')
    taille_id = request.form.get('id_taille','')
    couleur_id = request.form.get('id_couleur')
    mycursor = get_db().cursor()
    tuple_update = (stock, id_telephone, taille_id, couleur_id, id_declinaison_telephone)
    sql = '''UPDATE declinaison SET stock = %s, telephone_id = %s, taille_id = %s, couleur_id = %s
                 WHERE id_declinaison_telephone = %s'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    message = u'declinaison_velo modifié , id:' + str(id_declinaison_telephone) + '- stock :' + str(
        stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/telephone/edit?id_telephone=' + str(id_telephone))


@admin_declinaison_telephone.route('/admin/declinaison_telephone/delete', methods=['GET'])
def admin_delete_declinaison_telephone():
    mycursor = get_db().cursor()
    id_declinaison_telephone = request.args.get('id_declinaison_telephone', '')
    id_telephone = request.args.get('id_telephone', '')
    print("ID Déclinaison Téléphone:", id_declinaison_telephone)

    # Assurez-vous que id_declinaison_telephone n'est pas vide
    if not id_declinaison_telephone:
        flash('Identifiant de la déclinaison manquant.', 'alert-danger')
        return redirect('/admin/telephone/edit?id_telephone=' + id_telephone)

    sql = '''SELECT * FROM ligne_panier WHERE declinaison_id = %s'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    declinaisons_dans_panier = mycursor.fetchall()

    sql = '''SELECT * FROM ligne_commande WHERE declinaison_id = %s'''
    mycursor.execute(sql, (id_declinaison_telephone,))
    declinaisons_dans_commande = mycursor.fetchall()

    if declinaisons_dans_panier:
        flash('Il y a des exemplaires dans des paniers : vous ne pouvez pas le supprimer', 'alert-warning')
    elif declinaisons_dans_commande:
        flash('Il y a des exemplaires dans des commandes : vous ne pouvez pas le supprimer', 'alert-warning')
    else:
        sql = '''DELETE FROM declinaison WHERE id_declinaison_telephone = %s'''
        mycursor.execute(sql, (id_declinaison_telephone,))  # Corrigé ici
        get_db().commit()
        flash(u'Déclinaison supprimée avec succès, id_declinaison_telephone : ' + str(id_declinaison_telephone),
              'alert-success')

    return redirect('/admin/telephone/edit?id_telephone=' + str(id_telephone))

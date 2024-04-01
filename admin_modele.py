#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_modele = Blueprint('admin_modele', __name__,
                        template_folder='templates')

@admin_modele.route('/admin/modele/show')
def show_modele():
    mycursor = get_db().cursor()
    # sql = '''         '''
    # mycursor.execute(sql)
    # modeles = mycursor.fetchall()
    modeles=[]
    return render_template('admin/modele/show_modele.html', modeles=modeles)

@admin_modele.route('/admin/modele/add', methods=['GET'])
def add_modele():
    return render_template('admin/modele/add_modele.html')

@admin_modele.route('/admin/modele/add', methods=['POST'])
def valid_add_modele():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''         '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'modele ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/modele/show') #url_for('show_modele')

@admin_modele.route('/admin/modele/delete', methods=['GET'])
def delete_modele():
    id_modele = request.args.get('id_modele', '')
    mycursor = get_db().cursor()

    flash(u'suppression modele , id : ' + id_modele, 'alert-success')
    return redirect('/admin/modele/show')

@admin_modele.route('/admin/modele/edit', methods=['GET'])
def edit_modele():
    id_modele = request.args.get('id_modele', '')
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, (id_modele,))
    modele = mycursor.fetchone()
    return render_template('admin/modele/edit_modele.html', modele=modele)

@admin_modele.route('/admin/modele/edit', methods=['POST'])
def valid_edit_modele():
    libelle = request.form['libelle']
    id_modele = request.form.get('id_modele', '')
    tuple_update = (libelle, id_modele)
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'modele modifié, id: ' + id_modele + " libelle : " + libelle, 'alert-success')
    return redirect('/admin/modele/show')









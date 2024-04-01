#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_modele_stock():
    mycursor = get_db().cursor()

    # Requête SQL pour calculer le coût total du stock par type de casque
    sql = '''
        SELECT m.id_modele, m.libelle_modele,
               COALESCE(SUM(d.stock * d.prix_declinaison), 0) AS cout_total
        FROM modele m
        LEFT JOIN telephone t ON m.id_modele = t.modele_id
        LEFT JOIN declinaison d ON t.id_telephone = d.telephone_id
        GROUP BY m.id_modele, m.libelle_modele;
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()

    # Calcul du coût total de tous les stocks
    cout_total_stock = sum(row['cout_total'] for row in datas_show)

    # Extraction des étiquettes (labels) et des valeurs (values) pour le graphique
    labels = [row['libelle_modele'] for row in datas_show]
    values = [float(row['cout_total']) for row in datas_show]

    print("Data", datas_show)
    print("Labels", labels)
    print("Values", values)
    print("Coût total du stock", cout_total_stock)

    return render_template('admin/dataviz/dataviz_etat_1.html',
                           datas_show=datas_show, labels=labels, values=values, cout_total_stock=cout_total_stock)


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    # mycursor = get_db().cursor()
    # sql = '''    '''
    # mycursor.execute(sql)
    # adresses = mycursor.fetchall()

    #exemples de tableau "résultat" de la requête
    adresses =  [{'dep': '25', 'nombre': 1}, {'dep': '83', 'nombre': 1}, {'dep': '90', 'nombre': 3}]

    # recherche de la valeur maxi "nombre" dans les départements
    # maxAddress = 0
    # for element in adresses:
    #     if element['nbr_dept'] > maxAddress:
    #         maxAddress = element['nbr_dept']
    # calcul d'un coefficient de 0 à 1 pour chaque département
    # if maxAddress != 0:
    #     for element in adresses:
    #         indice = element['nbr_dept'] / maxAddress
    #         element['indice'] = round(indice,2)

    print(adresses)

    return render_template('admin/dataviz/dataviz_etat_map.html'
                           , adresses=adresses
                          )



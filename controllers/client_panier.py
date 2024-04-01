from flask import Blueprint, request, render_template, redirect, flash, session, abort
from datetime import datetime
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__, template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    utilisateur_id = session['id_user']
    id_telephone = request.form.get('id_telephone')
    quantite_panier = request.form.get('quantite')
    id_declinaison_telephone = request.form.get('id_declinaison_telephone')

    if id_declinaison_telephone is None:
        sql = '''SELECT *
                 FROM declinaison d
                 LEFT JOIN telephone t ON d.telephone_id = t.id_telephone
                 LEFT JOIN couleur ON d.couleur_id = couleur.id_couleur
                 LEFT JOIN taille ON d.taille_id = taille.id_taille
                 WHERE id_telephone = %s
            '''
        mycursor.execute(sql, (id_telephone,))
    else:
        sql = '''SELECT * FROM declinaison
                 WHERE id_declinaison_telephone = %s
            '''
        mycursor.execute(sql, (id_declinaison_telephone,))
    declinaisons = mycursor.fetchall()

    if len(declinaisons) == 1:
        id_declinaison_telephone = declinaisons[0]['id_declinaison_telephone']

        sql = """SELECT * FROM ligne_panier
                 WHERE utilisateur_id = %s AND declinaison_id = %s
                """
        mycursor.execute(sql, (utilisateur_id, id_declinaison_telephone))
        telephonepresent = mycursor.fetchone()
        if telephonepresent is None:
            sql = """INSERT INTO ligne_panier (utilisateur_id, declinaison_id, date_ajout, quantite) 
                     VALUES (%s, %s, NOW(), %s)"""
            mycursor.execute(sql, (utilisateur_id, id_declinaison_telephone, quantite_panier))
        else:
            sql = """UPDATE ligne_panier SET quantite = quantite + %s
                     WHERE declinaison_id = %s AND utilisateur_id = %s"""
            mycursor.execute(sql, (quantite_panier, id_declinaison_telephone, utilisateur_id))

        sql = """UPDATE declinaison SET stock = stock - %s
                 WHERE id_declinaison_telephone = %s"""
        mycursor.execute(sql, (quantite_panier, id_declinaison_telephone))

    elif len(declinaisons) == 0:
        flash('Problème de nombre de déclinaisons détecté.', 'alert-danger')
        return redirect('/client/telephone/show')
    else:
        sql = '''SELECT id_telephone, libelle_telephone, prix_telephone, image_telephone
                 FROM telephone
                 WHERE id_telephone = %s'''
        mycursor.execute(sql, (id_telephone,))
        telephone = mycursor.fetchone()

        return render_template('client/boutique/declinaison_telephone.html'
                               , declinaisons=declinaisons
                               , telephone=telephone)
    get_db().commit()
    return redirect('/client/telephone/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')
    if not id_client:
        flash('Vous devez être connecté pour effectuer cette action.', 'error')
        return redirect('/client/telephone/show')

    id_telephone = request.form.get('id_telephone')
    if not id_telephone:
        flash('Aucun téléphone spécifié pour la suppression.', 'error')
        return redirect('/client/telephone/show')

    # Réduire la quantité dans le panier par 1 et augmenter le stock, si quantité > 1
    sql_update_quantite = '''UPDATE ligne_panier SET quantite = quantite - 1 WHERE utilisateur_id = %s AND declinaison_id = %s AND quantite > 1;'''
    mycursor.execute(sql_update_quantite, (id_client, id_telephone))

    if mycursor.rowcount > 0:
        # Si la quantité a été réduite, réajuster le stock immédiatement
        sql_augmenter_stock = '''UPDATE declinaison SET stock = stock + 1 WHERE id_declinaison_telephone = %s;'''
        mycursor.execute(sql_augmenter_stock, (id_telephone,))
        flash('Un téléphone a été retiré du panier et le stock réajusté.', 'success')
    else:
        # Si la quantité n'était pas > 1, supprimer la ligne et réajuster le stock
        sql_delete_line = '''DELETE FROM ligne_panier WHERE utilisateur_id = %s AND declinaison_id = %s;'''
        mycursor.execute(sql_delete_line, (id_client, id_telephone))
        if mycursor.rowcount > 0:
            sql_augmenter_stock = '''UPDATE declinaison SET stock = stock + 1 WHERE id_declinaison_telephone = %s;'''
            mycursor.execute(sql_augmenter_stock, (id_telephone,))
            flash('Le dernier téléphone de ce modèle a été retiré du panier et le stock réajusté.', 'success')
        else:
            flash('Aucun changement effectué. Vérifiez que le téléphone est bien dans votre panier.', 'error')

    get_db().commit()
    return redirect('/client/telephone/show')

@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']

    sql_recup = '''SELECT declinaison_id, quantite FROM ligne_panier WHERE utilisateur_id = %s;'''
    mycursor.execute(sql_recup, (client_id,))
    telephones_panier = mycursor.fetchall()

    for telephone in telephones_panier:
        id_telephone = telephone['telephone_id']
        quantite = telephone['quantite']
        sql_augmenter_stock = '''UPDATE declinaison SET stock = stock + %s WHERE id_declinaison_telephone = %s;'''
        mycursor.execute(sql_augmenter_stock, (quantite, id_telephone))

    sql_vider_panier = ''' DELETE FROM ligne_panier WHERE utilisateur_id = %s; '''
    mycursor.execute(sql_vider_panier, (client_id,))
    get_db().commit()

    flash('Votre panier a été vidé.', 'success')
    return redirect('/client/telephone/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_telephone = request.form.get('id_telephone')

    sql_get_quantite = '''SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND declinaison_id = %s;'''
    mycursor.execute(sql_get_quantite, (id_client, id_telephone))
    result = mycursor.fetchone()

    if result:
        quantite = result['quantite']

        sql_augmenter_stock = '''UPDATE declinaison SET stock = stock + %s WHERE id_declinaison_telephone = %s;'''
        mycursor.execute(sql_augmenter_stock, (quantite, id_telephone))

        sql_delete_line = '''DELETE FROM ligne_panier WHERE utilisateur_id = %s AND declinaison_id = %s;'''
        mycursor.execute(sql_delete_line, (id_client, id_telephone))

        flash('Tous les téléphones de ce modèle ont été supprimés du panier et le stock a été réajusté.', 'success')
    else:
        flash('Aucun téléphone de ce modèle n\'a été trouvé dans votre panier.', 'error')

    get_db().commit()
    return redirect('/client/telephone/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    session['filter_word'] = request.form.get('filter_word', '').strip()
    session['filter_prix_min'] = request.form.get('filter_prix_min', '').strip()
    session['filter_prix_max'] = request.form.get('filter_prix_max', '').strip()
    session['filter_types'] = request.form.getlist('filter_types')
    return redirect('/client/telephone/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def supprimer_filtre():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    return redirect('/client/telephone/show')
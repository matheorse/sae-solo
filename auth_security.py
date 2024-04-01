#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session
import hashlib

from connexion_db import get_db

auth_security = Blueprint('auth_security', __name__,
                        template_folder='templates')

@auth_security.route('/login')
def auth_login():
    return render_template('auth/login.html')


@auth_security.route('/login', methods=['POST'])
def auth_login_post():
    mycursor = get_db().cursor()
    login = request.form.get('login')
    password = request.form.get('password')
    tuple_select = (login)
    sql = " SELECT * FROM utilisateur WHERE login=%s"
    retour = mycursor.execute(sql, (login))
    user = mycursor.fetchone()
    if user:
        passwordHash = hashlib.sha256(password.encode()).hexdigest()
        mdp_ok =  passwordHash == user["password"]
        if not mdp_ok:
            flash(u'Vérifier votre mot de passe et essayer encore.', 'alert-warning')
            return redirect('/login')
        else:
            session['login'] = user['login']
            session['role'] = user['role']
            session['id_user'] = user['id_utilisateur']
            print(user['login'], user['role'])
            if user['role'] == 'ROLE_admin':
                return redirect('/admin/commande/index')
            else:
                return redirect('/client/telephone/show')
    else:
        flash(u'Vérifier votre login et essayer encore.', 'alert-warning')
        return redirect('/login')

@auth_security.route('/signup')
def auth_signup():
    return render_template('auth/signup.html')


@auth_security.route('/signup', methods=['POST'])
def auth_signup_post():
    mycursor = get_db().cursor()
    email = request.form.get('email')
    login = request.form.get('login')
    password = request.form.get('password')

    sql_email = "SELECT * FROM utilisateur WHERE email=%s"
    mycursor.execute(sql_email, (email,))
    user_email = mycursor.fetchone()
    if user_email:
        flash(u'Votre adresse email existe déjà', 'alert-warning')
        return redirect('/signup')

    sql_login = "SELECT * FROM utilisateur WHERE login=%s"
    mycursor.execute(sql_login, (login,))
    user_login = mycursor.fetchone()
    if user_login:
        flash(u'Votre login existe déjà', 'alert-warning')
        return redirect('/signup')

    # ajouter un nouveau user
    password = hashlib.sha256(password.encode()).hexdigest()
    tuple_insert = (login, email, password, 'ROLE_client', login)
    sql = """  INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES(NULL, %s, %s, %s, %s, %s, '1')  """
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    sql = """  SELECT LAST_INSERT_ID() as last_insert_id"""
    mycursor.execute(sql)
    info_last_id = mycursor.fetchone()
    id_user = info_last_id['last_insert_id']
    print('last_insert_id', id_user)
    session.pop('login', None)
    session.pop('role', None)
    session.pop('id_user', None)
    session['login'] = login
    session['role'] = 'ROLE_client'
    session['id_user'] = id_user
    return redirect('/client/telephone/show')


@auth_security.route('/logout')
def auth_logout():
    session.pop('login', None)
    session.pop('role', None)
    session.pop('id_user', None)
    return redirect('/')

@auth_security.route('/forget-password', methods=['GET'])
def forget_password():
    return render_template('auth/forget_password.html')


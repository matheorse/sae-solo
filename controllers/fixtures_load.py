#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                          template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()


    drop_tables = [
        "ligne_commande", "ligne_panier", "commande", "telephone_couleur",
        "telephone", "couleur", "modele", "etat", "utilisateur"
    ]
    for table in drop_tables:
        sql = f'DROP TABLE IF EXISTS {table};'
        mycursor.execute(sql)


    sql = '''
        CREATE TABLE utilisateur (
            id_utilisateur INT AUTO_INCREMENT,
            login VARCHAR(255),
            password VARCHAR(255),
            role VARCHAR(255),
            est_actif tinyint(1),
            nom VARCHAR(255),
            email varchar(255),
            PRIMARY KEY (id_utilisateur)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
        CREATE TABLE etat (
            id_etat INT AUTO_INCREMENT,
            libelle_etat VARCHAR(50),
            PRIMARY KEY (id_etat)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
        CREATE TABLE couleur (
            id_couleur INT AUTO_INCREMENT,
            libelle_couleur VARCHAR(50),
            PRIMARY KEY (id_couleur)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
        CREATE TABLE modele (
            id_modele INT AUTO_INCREMENT,
            libelle_modele VARCHAR(50),
            PRIMARY KEY (id_modele)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
CREATE TABLE telephone(
   id_telephone INT AUTO_INCREMENT,
   libelle_telephone VARCHAR(255),
   stock_telephone INT,
   poids_telephone INT,
   taille_telephone INT,
   stockage_telephone INT,
   prix_telephone INT,
   autonomie_telephone INT,
   image_telephone VARCHAR(255),
   modele_id INT NOT NULL,
   PRIMARY KEY(id_telephone),
   FOREIGN KEY(modele_id) REFERENCES modele(id_modele)
) DEFAULT CHARSET=utf8mb4;
    '''
    mycursor.execute(sql)


    sql = '''
CREATE TABLE telephone_couleur(
   id_telephone INT NOT NULL,
   id_couleur INT NOT NULL,
   quantite INT NOT NULL,
   PRIMARY KEY(id_telephone, id_couleur),
   FOREIGN KEY(id_telephone) REFERENCES telephone(id_telephone),
   FOREIGN KEY(id_couleur) REFERENCES couleur(id_couleur)
) DEFAULT CHARSET=utf8mb4;
    '''
    mycursor.execute(sql)



    sql = '''
        CREATE TABLE commande (
            id_commande INT AUTO_INCREMENT,
            date_achat_commande DATE,
            utilisateur_id INT NOT NULL,
            etat_id INT NOT NULL,
            adresse_livraison VARCHAR(255),
            adresse_facturation VARCHAR(255),
            PRIMARY KEY (id_commande),
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
            FOREIGN KEY (etat_id) REFERENCES etat(id_etat)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
        CREATE TABLE ligne_panier (
            telephone_id INT,
            utilisateur_id INT,
            quantite INT,
            date_ajout DATE,
            PRIMARY KEY (telephone_id, utilisateur_id),
            FOREIGN KEY (telephone_id) REFERENCES telephone(id_telephone),
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
        CREATE TABLE ligne_commande (
            telephone_id INT,
            commande_id INT,
            prix INT,
            quantite INT,
            PRIMARY KEY (telephone_id, commande_id),
            FOREIGN KEY (telephone_id) REFERENCES telephone(id_telephone),
            FOREIGN KEY (commande_id) REFERENCES commande(id_commande)
        ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)


    sql = '''
        INSERT INTO utilisateur (id_utilisateur, login, email, password, role, nom, est_actif) VALUES
        (1, 'admin', 'admin@admin.fr', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'ROLE_admin', 'admin', 1),
        (2, 'client', 'client@client.fr', '948fe603f61dc036b5c596dc09fe3ce3f3d30dc90f024c85f3c82db2ccab679d', 'ROLE_client', 'client', 1),
        (3, 'client2', 'client2@client2.fr', '3f455143e75d1e7fd659dea57023496da3bd9f2f8908d1e2ac32641cd819d3e3', 'ROLE_client', 'client2', 1);
    '''
    mycursor.execute(sql)

    sql='''INSERT INTO etat (id_etat, libelle_etat) VALUES
        (1, 'Éxpédiée'),
        (2, 'En attente de validation'); '''
    mycursor.execute(sql)

    sql='''INSERT INTO couleur (id_couleur, libelle_couleur) VALUES
        (1, 'Noir'),
        (2, 'Blanc'),
        (3, 'Jaune'),
        (4, 'Rouge'),
        (5, 'Cyan'),
        (6, 'Marron'),
        (7, 'Bleu'),
        (8, 'Mauve'),
        (9, 'Vert'),
        (10, 'Gris');'''
    mycursor.execute(sql)

    sql='''INSERT INTO modele (id_modele, libelle_modele) VALUES
    (1, 'Standard'),
    (2, 'Modèle Pro'),
    (3, 'Modèle Max'),
    (4, 'Modèle S');'''
    mycursor.execute(sql)

    sql = ''' INSERT INTO telephone (id_telephone, libelle_telephone, stock_telephone, poids_telephone, taille_telephone, stockage_telephone, prix_telephone, autonomie_telephone, image_telephone, modele_id) VALUES
(1, 'Mait Ace 15 Pro', 150, 10, 5, 64, 1229, 12, "titaneface.jpg", 2),
(2, 'Mait Ace 15 Max', 150, 10, 5, 64, 1129, 12, "Ace15Max_gris_face.jpg", 3),
(3, 'Mait Ace 15', 170, 30, 5.5, 128, 969, 14, "Ace15noirface.jpg", 1),
(4, 'Mait Ace 15 S', 170, 30, 5.5, 128, 969, 14, "Ace15noirface.jpg", 4),

(5, 'Mait Ace 14 Pro', 160, 70, 5.2, 256, 869, 13, "Ace14bleuface.jpg", 2),
(6, 'Mait Ace 14 Max', 160, 70, 5.2, 256, 869, 13, "Ace14bleuface.jpg", 3),
(7, 'Mait Ace 14', 160, 70, 5.2, 256, 869, 13, "Ace14bleuface.jpg", 1),
(8, 'Mait Ace 14 S', 160, 70, 5.2, 256, 869, 13, "Ace14bleuface.jpg", 4),

(9, 'Mait Ace 13 Pro', 180, 5, 5.7, 128, 749, 15, "Ace13vertface.jpg", 2),
(10, 'Mait Ace 13 Max', 180, 5, 5.7, 128, 749, 15, "Ace13vertface.jpg", 3),
(11, 'Mait Ace 13', 180, 5, 5.7, 128, 749, 15, "Ace13vertface.jpg", 1),
(12, 'Mait Ace 13 S', 180, 5, 5.7, 128, 749, 15, "Ace13vertface.jpg", 4),

(13, 'Mait Ace SE Pro', 155, 20, 6.0, 64, 529, 12, "SErougeface.jpg", 2),
(14, 'Mait Ace SE', 155, 20, 6.0, 64, 529, 12, "SErougeface.jpg", 1),

(15, 'Mait One Pro', 165, 90, 5.1, 512, 1129, 16, "OnePronoirface.jpg", 2),
(16, 'Mait One Max', 165, 90, 5.1, 512, 1129, 16, "OnePronoirface.jpg", 3),
(17, 'Mait One', 165, 90, 5.1, 512, 1129, 16, "OnePronoirface.jpg", 1),
(18, 'Mait One S', 165, 90, 5.1, 512, 1129, 16, "OnePronoirface.jpg", 4);'''
    mycursor.execute(sql)

    sql = ''' INSERT INTO telephone_couleur (id_telephone, id_couleur, quantite) VALUES
    (1, 2, 150),
    (1, 3, 99),
    (3, 3, 160),
    (4, 1, 180),
    (5, 4, 155),
    (6, 2, 165),
    (7, 5, 170),
    (8, 6, 175),
    (9, 1, 160),
    (10, 4, 185),
    (11, 2, 150),
    (12, 7, 165),
    (13, 8, 175),
    (14, 1, 160),
    (15, 9, 170);'''
    mycursor.execute(sql)





    sql='''INSERT INTO commande (date_achat_commande, utilisateur_id, etat_id, adresse_livraison, adresse_facturation) VALUES
        ('2024-02-01', 1, 1, '123 Rue de la Paix, 75001 Paris, France', '123 Rue de la Paix, 75001 Paris, France'),
        ('2024-02-03', 1, 2, '456 Boulevard des Capucines, 75002 Paris, France', '456 Boulevard des Capucines, 75002 Paris, France'),
        ('2024-02-04', 2, 1, '789 Avenue Montaigne, 75008 Paris, France', '789 Avenue Montaigne, 75008 Paris, France'),
        ('2024-02-05', 1, 1, '1011 Rue du Faubourg Saint-Honoré, 75008 Paris, France', '50 Rue de lUniversité, 75007 Paris, France'),
        ('2024-02-06', 2, 2, '1213 Rue de Rivoli, 75001 Paris, France', '5 Rue de la Paix, 75002 Paris, France');'''
    mycursor.execute(sql)

    sql='''INSERT INTO ligne_panier (telephone_id, utilisateur_id, quantite, date_ajout) VALUES
   (7, 1, 2, '2024-02-01'),
    (8, 2, 1, '2024-02-02'),
    (9, 1, 3, '2024-02-03'),
    (10, 2, 2, '2024-02-04'),
    (11, 1, 1, '2024-02-05'),
    (12, 2, 4, '2024-02-06');'''
    mycursor.execute(sql)

    sql=''' INSERT INTO ligne_commande (telephone_id, commande_id, prix, quantite) VALUES
    (7, 1, 650, 2),
    (8, 1, 700, 1),
    (9, 2, 600, 3),
    (10, 3, 850, 2),
    (11, 4, 500, 1),
    (12, 5, 1400, 4);'''
    mycursor.execute(sql)

    get_db().commit()
    return redirect('/')


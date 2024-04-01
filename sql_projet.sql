DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS declinaison;
DROP TABLE IF EXISTS telephone;
DROP TABLE IF EXISTS couleur;
DROP TABLE IF EXISTS modele;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS taille;

-- Création des tables
CREATE TABLE taille(
    id_taille INT AUTO_INCREMENT,
    libelle_taille VARCHAR(50),
    PRIMARY KEY(id_taille)
);

CREATE TABLE utilisateur(
    id_utilisateur INT AUTO_INCREMENT,
    login VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(255),
    est_actif TINYINT(1),
    nom VARCHAR(255),
    email VARCHAR(255),
    PRIMARY KEY (id_utilisateur)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE etat(
   id_etat INT AUTO_INCREMENT,
   libelle_etat VARCHAR(255),
   PRIMARY KEY(id_etat)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE couleur(
   id_couleur INT AUTO_INCREMENT,
   libelle_couleur VARCHAR(255),
   PRIMARY KEY(id_couleur)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE modele(
   id_modele INT AUTO_INCREMENT,
   libelle_modele VARCHAR(255),
   PRIMARY KEY(id_modele)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE telephone(
   id_telephone INT AUTO_INCREMENT,
   libelle_telephone VARCHAR(255),
   poids_telephone INT,
   stockage_telephone INT,
   prix_telephone INT,
   autonomie_telephone INT,
   image_telephone VARCHAR(255),
   modele_id INT NOT NULL,
   PRIMARY KEY(id_telephone),
   FOREIGN KEY(modele_id) REFERENCES modele(id_modele)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE declinaison (
    id_declinaison_telephone INT AUTO_INCREMENT,
    stock INT,
    prix_declinaison DECIMAL(10,2),
    telephone_id INT,
    taille_id INT NOT NULL,
    couleur_id INT NOT NULL,
    PRIMARY KEY (id_declinaison_telephone),
    FOREIGN KEY (telephone_id) REFERENCES telephone(id_telephone),
    FOREIGN KEY (taille_id) REFERENCES taille(id_taille),
    FOREIGN KEY (couleur_id) REFERENCES couleur(id_couleur)
);

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat_commande DATE,
   utilisateur_id INT NOT NULL,
   etat_id INT NOT NULL,
   adresse_livraison VARCHAR(255),
   adresse_facturation VARCHAR(255),
   PRIMARY KEY(id_commande),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(etat_id) REFERENCES etat(id_etat)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE ligne_panier(
   declinaison_id INT,
   utilisateur_id INT,
   quantite INT,
   date_ajout DATE,
   PRIMARY KEY(declinaison_id, utilisateur_id),
   FOREIGN KEY(declinaison_id) REFERENCES declinaison(id_declinaison_telephone),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE ligne_commande(
   declinaison_id INT,
   commande_id INT,
   prix INT,
   quantite INT,
   PRIMARY KEY(declinaison_id, commande_id),
   FOREIGN KEY(declinaison_id) REFERENCES declinaison(id_declinaison_telephone),
   FOREIGN KEY(commande_id) REFERENCES commande(id_commande)
) DEFAULT CHARSET=utf8mb4;

-- Insertion des données
INSERT INTO utilisateur(login, email, password, role, nom, est_actif) VALUES
('admin', 'admin@admin.fr', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'ROLE_admin', 'admin', 1),
('client', 'client@client.fr', '948fe603f61dc036b5c596dc09fe3ce3f3d30dc90f024c85f3c82db2ccab679d', 'ROLE_client', 'client', 1),
('client2', 'client2@client2.fr', '3f455143e75d1e7fd659dea57023496da3bd9f2f8908d1e2ac32641cd819d3e3', 'ROLE_client', 'client2', 1);

INSERT INTO etat(libelle_etat) VALUES
('Expédiée'),
('En attente de validation');

INSERT INTO couleur(libelle_couleur) VALUES
('Noir'),
('Blanc'),
('Jaune'),
('Rouge'),
('Cyan'),
('Marron'),
('Bleu'),
('Mauve'),
('Vert'),
('Gris');

INSERT INTO modele(libelle_modele) VALUES
('Standard'),
('Modèle Pro'),
('Modèle Max'),
('Modèle S');

-- Correction et continuation des INSERT INTO pour la table `telephone`
INSERT INTO telephone (libelle_telephone, poids_telephone, stockage_telephone, prix_telephone, autonomie_telephone, image_telephone, modele_id) VALUES
('Mait Ace 15 Pro', 150, 64, 1229, 12, 'titaneface.jpg', 2),
('Mait Ace 15 Max', 150, 64, 1129, 12, 'Ace15Max_gris_face.jpg', 3),
('Mait Ace 15', 170, 128, 969, 14, 'Ace15noirface.jpg', 1),
('Mait Ace 15 S', 170, 128, 969, 14, 'Ace15noirface.jpg', 4),
('Mait Ace 14 Pro', 160, 256, 869, 13, 'Ace14bleuface.jpg', 2),
('Mait Ace 14 Max', 160, 256, 869, 13, 'Ace14bleuface.jpg', 3),
('Mait Ace 14', 160, 256, 869, 13, 'Ace14bleuface.jpg', 1),
('Mait Ace 14 S', 160, 256, 869, 13, 'Ace14bleuface.jpg', 4),
('Mait Ace 13 Pro', 180, 128, 749, 15, 'Ace13vertface.jpg', 2),
('Mait Ace 13 Max', 180, 128, 749, 15, 'Ace13vertface.jpg', 3),
('Mait Ace 13', 180, 128, 749, 15, 'Ace13vertface.jpg', 1),
('Mait Ace 13 S', 180, 128, 749, 15, 'Ace13vertface.jpg', 4),
('Mait Ace SE Pro', 155, 64, 529, 12, 'SErougeface.jpg', 2),
('Mait Ace SE', 155, 64, 529, 12, 'SErougeface.jpg', 1),
('Mait One Pro', 165, 512, 1129, 16, 'OnePronoirface.jpg', 2),
('Mait One Max', 165, 512, 1129, 16, 'OnePronoirface.jpg', 3),
('Mait One', 165, 512, 1129, 16, 'OnePronoirface.jpg', 1),
('Mait One S', 165, 512, 1129, 16, 'OnePronoirface.jpg', 4);

-- Insertion de données pour la table `taille`
INSERT INTO taille(libelle_taille) VALUES
('Petit'),
('Moyen'),
('Grand');

-- Exemple d'insertion pour la table `declinaison`
INSERT INTO declinaison (stock, prix_declinaison, telephone_id, taille_id, couleur_id) VALUES
(10, 1299.99, 1, 1, 1),
(10, 1399.99, 1, 2, 1),
(10, 1299.99, 1, 1, 2),
(0, 1399.99, 2, 2, 2),
(10, 1399.99, 2, 1, 2),
(0, 1149.99, 3, 3, 3);

-- Insertion de données pour la table `commande`
INSERT INTO commande (date_achat_commande, utilisateur_id, etat_id, adresse_livraison, adresse_facturation) VALUES
('2024-02-01', 1, 1, '123 Rue de la Paix, 75001 Paris, France', '123 Rue de la Paix, 75001 Paris, France'),
('2024-02-03', 1, 2, '456 Boulevard des Capucines, 75002 Paris, France', '456 Boulevard des Capucines, 75002 Paris, France'),
('2024-02-04', 2, 1, '789 Avenue Montaigne, 75008 Paris, France', '789 Avenue Montaigne, 75008 Paris, France'),
('2024-02-05', 1, 1, '1011 Rue du Faubourg Saint-Honoré, 75008 Paris, France', '50 Rue de lUniversité, 75007 Paris, France'),
('2024-02-06', 2, 2, '1213 Rue de Rivoli, 75001 Paris, France', '5 Rue de la Paix, 75002 Paris, France');

-- Insertion de données pour la table `ligne_panier`
INSERT INTO ligne_panier(declinaison_id, utilisateur_id, quantite, date_ajout) VALUES
(1, 1, 2, '2024-02-01'),
(2, 2, 1, '2024-02-02'),
(3, 1, 3, '2024-02-03'),
(4, 1, 1, '2024-02-05'),
(5, 2, 4, '2024-02-06');

-- Insertion de données pour la table `ligne_commande`
INSERT INTO ligne_commande(declinaison_id, commande_id, prix, quantite) VALUES
(4, 1, 650, 2),
(5, 1, 700, 1),
(1, 3, 850, 2),
(3, 4, 500, 1),
(2, 5, 1400, 4);

SELECT * FROM declinaison

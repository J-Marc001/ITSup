🛠️ Système de Gestion des Demandes de Maintenance (Helpdesk)
Une application Full-Stack développée en Python (Flask) et MySQL pour gérer les incidents informatiques au sein d'une entreprise ou d'une université.
📋 Fonctionnalités
Authentification : Connexion et inscription sécurisées.
Rôles Utilisateurs :
👤 Employé : Crée des tickets et suit leur avancement.
🔧 Technicien : Voit les tickets assignés, change les statuts et ajoute des rapports.
👑 Administrateur : Gère les utilisateurs, assigne les tickets et a une vue globale.
Gestion des Tickets : Création, modification, priorisation et catégorisation.
Système de Commentaires : Discussion sur chaque ticket.
Interface Admin : Panneau pour modifier les rôles des utilisateurs.
⚙️ Prérequis
Avant de commencer, assurez-vous d'avoir installé :
Python 3.x : Télécharger ici
XAMPP (pour le serveur MySQL) : Télécharger ici
Un éditeur de code (VS Code recommandé).
🚀 Installation
1. Cloner ou télécharger le projet
Placez les fichiers dans un dossier, par exemple Projet_Maintenance.
2. Installer les dépendances Python
Ouvrez votre terminal dans le dossier du projet et exécutez :
      pip install flask flask-sqlalchemy flask-login pymysql werkzeug
🗄️ Configuration de la Base de Données (XAMPP)
1. Démarrer XAMPP
Lancez XAMPP Control Panel.
Démarrez Apache et MySQL (boutons "Start").
Note : Si Apache ne démarre pas à cause du port 80, configurez-le sur le port 8080.
2. Créer la base de données
Ouvrez votre navigateur sur http://localhost/phpmyadmin (ou http://localhost:8080/phpmyadmin).
Cliquez sur Nouvelle base de données.
Nommez-la : maintenance_db.
Cliquez sur Créer.
3. Importer la structure SQL
Cliquez sur l'onglet SQL dans phpMyAdmin et collez le script suivant pour créer les tables et les données de base :
-- CRÉATION DES TABLES
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
) ENGINE=InnoDB;

CREATE TABLE status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    color VARCHAR(20)
) ENGINE=InnoDB;

CREATE TABLE priority (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    level INT
) ENGINE=InnoDB;

CREATE TABLE ticket (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category_id INT NOT NULL,
    priority_id INT NOT NULL,
    status_id INT DEFAULT 1,
    requester_id INT NOT NULL,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at DATETIME,
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (priority_id) REFERENCES priority(id),
    FOREIGN KEY (status_id) REFERENCES status(id),
    FOREIGN KEY (requester_id) REFERENCES user(id),
    FOREIGN KEY (assigned_to) REFERENCES user(id)
) ENGINE=InnoDB;

CREATE TABLE comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES ticket(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB;

-- DONNÉES OBLIGATOIRES
INSERT INTO status (name, color) VALUES 
('En attente', 'warning'), ('En cours', 'primary'), ('Résolue', 'success');

INSERT INTO priority (name, level) VALUES 
('Faible', 1), ('Moyenne', 2), ('Élevée', 3);

INSERT INTO category (name, description) VALUES 
('Matériel', 'PC, Écran, Imprimante'), 
('Logiciel', 'Office, Windows, ERP'), 
('Réseau', 'Wifi, Internet, VPN');

🏁 Démarrage de l'application
Assurez-vous que la connexion à la base de données dans app.py est correcte :
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/maintenance_db"
(Si vous avez mis un mot de passe à MySQL sur XAMPP, ajoutez-le après root:).
Lancez le serveur Python :
    Bash : python app.py

Ouvrez votre navigateur à l'adresse :
👉 http://127.0.0.1:5000

Créer le premier Administrateur
Par défaut, l'inscription crée un compte "EMPLOYEE". Pour créer votre premier Admin :
Allez sur le site et cliquez sur "Créer un compte".
Inscrivez-vous (ex: admin / admin@test.com).
Allez dans phpMyAdmin > Table user.
Trouvez votre utilisateur, cliquez sur Éditer.
Changez la valeur de la colonne role de EMPLOYEE à ADMIN.
Cliquez sur Exécuter.
Reconnectez-vous sur le site : vous avez maintenant accès au menu "Gestion Utilisateurs".

📂 Structure du Projet
/Projet_Maintenance
│
├── app.py                 # Le cœur de l'application (Backend Flask)
├── README.md              # Documentation
│
└── templates/             # Dossier des pages HTML
    ├── base.html          # Squelette commun (Navbar, Footer)
    ├── login.html         # Page de connexion
    ├── register.html      # Page d'inscription
    ├── dashboard.html     # Tableau de bord (Tickets)
    ├── create_ticket.html # Formulaire de création
    ├── ticket_detail.html # Vue détaillée et traitement
    ├── admin_users.html   # Liste des utilisateurs (Admin)
    └── edit_user.html     # Modification utilisateur (Admin)

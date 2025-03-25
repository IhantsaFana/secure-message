CREATE DATABASE IF NOT EXISTS message;
USE message;

CREATE TABLE Utilisateur (
  IDUtilisateur INT AUTO_INCREMENT PRIMARY KEY,
  Nom VARCHAR(255) NOT NULL,
  Prenom VARCHAR(255) NOT NULL,
  Email VARCHAR(255) NOT NULL UNIQUE,
  MotDePasse VARCHAR(255) NOT NULL,
  DateInscription DATETIME DEFAULT CURRENT_TIMESTAMP,
  Statut ENUM('en ligne', 'hors ligne') DEFAULT 'hors ligne',
  PhotoProfile VARCHAR(255)
);

CREATE TABLE Conversation (
  IDConversation INT AUTO_INCREMENT PRIMARY KEY,
  Titre VARCHAR(255),
  Type ENUM('privée', 'groupe') NOT NULL,
  DateCreation DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Message (
  IDMessage INT AUTO_INCREMENT PRIMARY KEY,
  Contenu TEXT NOT NULL,
  DateHeureEnvoi DATETIME DEFAULT CURRENT_TIMESTAMP,
  Statut ENUM('envoyé', 'livré', 'lu') DEFAULT 'envoyé',
  TypeMessage ENUM('texte', 'image', 'vidéo', 'fichier') DEFAULT 'texte',
  FK_Utilisateur INT NOT NULL,
  FK_Conversation INT NOT NULL,
  FOREIGN KEY (FK_Utilisateur) REFERENCES Utilisateur(IDUtilisateur),
  FOREIGN KEY (FK_Conversation) REFERENCES Conversation(IDConversation)
);

CREATE TABLE Participation (
  IDParticipation INT AUTO_INCREMENT PRIMARY KEY,
  DateRejoint DATETIME DEFAULT CURRENT_TIMESTAMP,
  Role ENUM('admin', 'membre') DEFAULT 'membre',
  FK_Utilisateur INT NOT NULL,
  FK_Conversation INT NOT NULL,
  FOREIGN KEY (FK_Utilisateur) REFERENCES Utilisateur(IDUtilisateur),
  FOREIGN KEY (FK_Conversation) REFERENCES Conversation(IDConversation)
);

CREATE TABLE Reaction (
  IDReaction INT AUTO_INCREMENT PRIMARY KEY,
  TypeReaction ENUM('like', 'love', 'dislike') DEFAULT 'like',
  DateReaction DATETIME DEFAULT CURRENT_TIMESTAMP,
  FK_Utilisateur INT NOT NULL,
  FK_Message INT NOT NULL,
  FOREIGN KEY (FK_Utilisateur) REFERENCES Utilisateur(IDUtilisateur),
  FOREIGN KEY (FK_Message) REFERENCES Message(IDMessage)
);

CREATE TABLE FichierJoint (
  IDFichier INT AUTO_INCREMENT PRIMARY KEY,
  NomFichier VARCHAR(255),
  CheminAcces VARCHAR(255),
  TypeFichier VARCHAR(50),
  Taille INT,
  FK_Message INT NOT NULL,
  FOREIGN KEY (FK_Message) REFERENCES Message(IDMessage)
);

CREATE DATABASE IF NOT EXISTS data_base;
USE data_base;

--Esto solamente para poder probarlo de momento
DROP TABLE IF EXISTS predicciones;
DROP TABLE IF EXISTS partidos;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE partidos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
);

INSERT INTO partidos (id)
VALUES
    (1),
    (2),
    (3);


CREATE TABLE usuarios(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre varchar(40),
    puntos int unsigned default 0,
    mail varchar(40)
);

INSERT INTO usuarios (nombre, puntos, mail) 
VALUES
    ("juanito",0,"ElMasCapito123@yahoo.com"),
    ("manuelita",9,"pehuajo@gmail.com"),
    ("Pablo",3,"clavito@gmail.com"),
    ("luna",1,"luna@gmail.com"),
    ("valentin",7,"valentin@gmail.com");


CREATE TABLE predicciones(
    predicciones_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    partido_id INT NOT NULL,
    goles_local INT UNSIGNED DEFAULT 0,
    goles_visitante INT UNSIGNED DEFAULT 0,

    CONSTRAINT chk_goles_positivos CHECK (goles_local >= 0 AND goles_visitante >= 0),

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (partido_id) REFERENCES partidos(id)
);

INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante)
VALUES
    (1, 1,1, 2),
    (2, 3, 0, 1),
    (3, 2, 0, 0);

SELECT * FROM predicciones;
SELECT * FROM partidos;
SELECT * FROM usuarios;

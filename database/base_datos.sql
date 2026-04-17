CREATE DATABASE IF NOT EXISTS data_base;
USE data_base;

--Esto solamente para poder probarlo de momento
DROP TABLE IF EXISTS predicciones;
DROP TABLE IF EXISTS partidos;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE partidos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    equipo_local VARCHAR(100) NOT NULL,
    equipo_visitante VARCHAR(100) NOT NULL,
    estadio VARCHAR(100),
    ciudad VARCHAR(100),
    fecha DATETIME,
    fase VARCHAR(50) NOT NULL,
    gol_local INT DEFAULT NULL,
    gol_visitante INT DEFAULT NULL
);
-- Insertar partidos de prueba (Nota: debe ir antes de las predicciones)
INSERT INTO partidos (equipo_local, equipo_visitante, estadio, ciudad, fecha, fase, gol_local, gol_visitante)
VALUES
    ('Argentina', 'Francia', 'Lusail', 'Doha', '2026-06-15 15:00:00', 'Final', '3', '3'),
    ('Brasil', 'Uruguay', 'Centenario', 'Montevideo', '2026-06-16 18:00:00', 'Grupos','2','0'),
    ('España', 'Alemania', 'Santiago Bernabéu', 'Madrid', '2026-06-17 21:00:00', 'Semis','1','2');


CREATE TABLE usuarios(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre varchar(40),
    puntos int unsigned default 0,
    mail varchar(40)
);

INSERT INTO usuarios (nombre, puntos, email) 
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

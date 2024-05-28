CREATE TABLE `decks` (
  `idDeck` int NOT NULL AUTO_INCREMENT,
  `deck_name` varchar(100) NOT NULL,
  `idUsuario` int NOT NULL,
  PRIMARY KEY (`idDeck`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `idUsuario` FOREIGN KEY (`idUsuario`) REFERENCES `usuarios` (`idUsuarios`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
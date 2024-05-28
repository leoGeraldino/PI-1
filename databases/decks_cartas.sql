CREATE TABLE `decks_cartas` (
  `iddecks_cartas` int NOT NULL AUTO_INCREMENT,
  `idDeck` int NOT NULL,
  `idCarta` int NOT NULL,
  PRIMARY KEY (`iddecks_cartas`),
  KEY `idDeck_idx` (`idDeck`) /*!80000 INVISIBLE */,
  KEY `idCarta_idx` (`idCarta`),
  CONSTRAINT `idCarta` FOREIGN KEY (`idCarta`) REFERENCES `cartas` (`idCarta`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idDeck` FOREIGN KEY (`idDeck`) REFERENCES `decks` (`idDeck`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
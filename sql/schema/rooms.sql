DROP TABLE IF EXISTS rooms;
CREATE TABLE rooms (
	idRoom INT(5) NOT NULL AUTO_INCREMENT PRIMARY KEY,
	name CHAR(20) NOT NULL,
	owneruser CHAR(40) NOT NULL,
	secretpin INT(4),
	codCategory SMALLINT(5),
	UNIQUE(name) 
);

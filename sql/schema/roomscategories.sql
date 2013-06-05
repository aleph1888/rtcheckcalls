DROP TABLE IF EXISTS rooms_categories;
CREATE TABLE rooms_categories (
	idCategory INT(5) NOT NULL AUTO_INCREMENT PRIMARY KEY,
	categoryname CHAR(20) NOT NULL,
	codCategoryParent SMALLINT(5),
	UNIQUE(categoryname) 
);

BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "ingredient" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"unit_type"	INTEGER NOT NULL,
	"category_type"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "recipe" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"source"	TEXT,
	"prep_time"	INTEGER,
	"total_time"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "recipe_ingredient" (
	"recipe_id"	INTEGER NOT NULL,
	"ingredient_id"	INTEGER NOT NULL,
	"amount"	REAL NOT NULL,
	"required"	INTEGER NOT NULL,
	FOREIGN KEY("ingredient_id") REFERENCES "ingredient"("id"),
	FOREIGN KEY("recipe_id") REFERENCES "recipe"("id")
);
CREATE TABLE IF NOT EXISTS "recipe_instruction" (
	"recipe_id"	INTEGER NOT NULL UNIQUE,
	"step_number"	INTEGER NOT NULL,
	"instructions"	TEXT,
	PRIMARY KEY("recipe_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "recipe_nutrient" (
	"recipe_id"	INTEGER NOT NULL,
	"calories"	INTEGER,
	"fat"	INTEGER,
	"sat_fat"	INTEGER,
	"carbs"	INTEGER,
	"sugar"	INTEGER,
	"fibre"	INTEGER,
	"protein"	INTEGER,
	"salt"	INTEGER,
	CONSTRAINT "FK" FOREIGN KEY("recipe_id") REFERENCES "recipe"("id")
);
COMMIT;

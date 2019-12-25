CREATE OR REPLACE FUNCTION update_modified_column()   
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified = NOW();
    RETURN NEW;   
END;
$$ language 'plpgsql';

CREATE TABLE IF NOT EXISTS wizard (
	id SERIAL PRIMARY KEY,
	sub TEXT NOT NULL UNIQUE,
	username TEXT NOT NULL,
	xp INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS spell (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	url TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS wizard_spell (
	wizard INT REFERENCES wizard(id),
	spell INT REFERENCES spell(id),
	PRIMARY KEY (wizard, spell)
);


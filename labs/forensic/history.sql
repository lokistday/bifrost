-- Original synthetic schema, not a real browser's database schema or epoch.
CREATE TABLE visits(id TEXT PRIMARY KEY, time TEXT NOT NULL, url TEXT NOT NULL, transition TEXT NOT NULL);
INSERT INTO visits VALUES('B01','2026-10-01T00:00:00+00:00','https://training.invalid/notes','typed');
INSERT INTO visits VALUES('B02','2026-10-01T00:00:20+00:00','https://training.invalid/manual','link');
INSERT INTO visits VALUES('B03','2026-10-01T00:00:25+00:00','https://training.invalid/assets/icon','auto');

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(64) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128), 
	created_at DATETIME, 
	last_seen DATETIME, 
	is_admin BOOLEAN, 
	games_played INTEGER, 
	games_won INTEGER, 
	best_score INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
INSERT INTO users VALUES(1,'falzy_frosh05','fawassurajudeen16@gmail.com','pbkdf2:sha256:600000$5DYVxNGgOivr3vqb$fd8cb5d046cd64ca804a4ced834ae4d5116b17266976673e7cedb96bd5a951b8','2025-05-03 06:37:14.215556','2025-05-03 06:37:14.215556',0,7,6,180);
INSERT INTO users VALUES(2,'Kante','Ayo@gmail.com','pbkdf2:sha256:600000$WVl8zzylPtNrs0wL$abe0fb902fc891a8d3f96ccd9120cd123e17ffcd33ff8e479b8c7604e61ff247','2025-05-03 23:08:46.761558','2025-05-03 23:08:46.761558',0,0,0,0);
CREATE TABLE game_sessions (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	level VARCHAR(20), 
	secret_number INTEGER, 
	attempts_left INTEGER, 
	current_range_low INTEGER, 
	current_range_high INTEGER, 
	completed BOOLEAN, 
	won BOOLEAN, 
	score INTEGER, 
	created_at DATETIME, 
	end_time DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO game_sessions VALUES(1,1,'easy',93,10,1,100,0,0,0,'2025-05-03 10:07:22.779056',NULL);
INSERT INTO game_sessions VALUES(2,1,'medium',177,15,1,1000,0,0,0,'2025-05-03 10:07:33.859382',NULL);
INSERT INTO game_sessions VALUES(3,1,'hard',8184,20,1,10000,0,0,0,'2025-05-03 10:07:40.434142',NULL);
INSERT INTO game_sessions VALUES(4,1,'easy',91,10,1,100,0,0,0,'2025-05-03 10:09:03.732716',NULL);
INSERT INTO game_sessions VALUES(5,1,'easy',9,4,6,10,0,0,0,'2025-05-03 10:30:31.014019',NULL);
INSERT INTO game_sessions VALUES(6,1,'medium',4,7,1,50,0,0,0,'2025-05-03 10:34:03.821358',NULL);
INSERT INTO game_sessions VALUES(7,1,'hard',53,10,1,100,0,0,0,'2025-05-03 10:34:12.674368',NULL);
INSERT INTO game_sessions VALUES(8,1,'easy',4,5,1,10,0,0,0,'2025-05-03 10:54:38.406015',NULL);
INSERT INTO game_sessions VALUES(9,1,'easy',2,5,1,10,0,0,0,'2025-05-03 10:59:00.179143',NULL);
INSERT INTO game_sessions VALUES(10,1,'easy',1,5,1,10,0,0,0,'2025-05-03 11:21:23.095706',NULL);
INSERT INTO game_sessions VALUES(11,1,'easy',1,5,1,10,0,0,0,'2025-05-03 20:21:28.146302',NULL);
INSERT INTO game_sessions VALUES(12,1,'easy',7,5,1,10,0,0,0,'2025-05-03 21:08:59.902487',NULL);
INSERT INTO game_sessions VALUES(13,1,'easy',3,5,1,10,0,0,0,'2025-05-03 21:24:09.591514',NULL);
INSERT INTO game_sessions VALUES(14,1,'easy',10,4,8,10,0,0,0,'2025-05-03 21:33:50.386151',NULL);
INSERT INTO game_sessions VALUES(15,1,'easy',9,4,8,10,0,0,0,'2025-05-03 21:34:28.223629',NULL);
INSERT INTO game_sessions VALUES(16,1,'easy',10,1,10,10,0,0,0,'2025-05-03 21:49:22.708129',NULL);
INSERT INTO game_sessions VALUES(17,1,'medium',49,6,36,50,0,0,0,'2025-05-03 21:51:21.263623',NULL);
INSERT INTO game_sessions VALUES(18,1,'easy',3,2,3,3,0,0,0,'2025-05-03 21:52:59.280388',NULL);
INSERT INTO game_sessions VALUES(19,1,'easy',3,3,1,6,1,1,30,'2025-05-03 21:58:54.915806','2025-05-03 21:59:03.926979');
INSERT INTO game_sessions VALUES(20,1,'easy',2,2,1,2,1,1,20,'2025-05-03 22:06:41.093908','2025-05-03 22:06:54.620075');
INSERT INTO game_sessions VALUES(21,1,'easy',5,2,4,6,1,1,20,'2025-05-03 22:18:33.110277','2025-05-03 22:18:45.418298');
INSERT INTO game_sessions VALUES(22,1,'medium',16,0,16,16,1,0,0,'2025-05-03 22:19:24.368400','2025-05-03 22:20:22.124570');
INSERT INTO game_sessions VALUES(23,1,'medium',42,2,41,44,1,1,60,'2025-05-03 22:20:51.481421','2025-05-03 22:21:26.045315');
INSERT INTO game_sessions VALUES(24,1,'hard',48,3,48,48,1,1,180,'2025-05-03 22:21:56.394251','2025-05-03 22:22:32.751306');
INSERT INTO game_sessions VALUES(25,1,'hard',82,3,81,82,1,1,180,'2025-05-03 22:53:39.521755','2025-05-03 22:54:47.485149');
CREATE TABLE feedback (
	id INTEGER NOT NULL, 
	name VARCHAR(64), 
	email VARCHAR(120), 
	message TEXT, 
	user_id INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO feedback VALUES(1,'Fawas Surajudeen','fawassurajudeen16@gmail.com','The game is a great game, but it is still having some slight issue if you can fix that it will be good',1,'2025-05-03 22:45:27.152190');
INSERT INTO feedback VALUES(2,'Fawas Surajudeen','fawassurajudeen16@gmail.com','The game was nice≡ƒÑ░',1,'2025-05-03 22:56:21.227670');
CREATE TABLE guesses (
	id INTEGER NOT NULL, 
	game_id INTEGER, 
	guess_value INTEGER, 
	result VARCHAR(20), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(game_id) REFERENCES game_sessions (id)
);
INSERT INTO guesses VALUES(1,5,5,'too low','2025-05-03 10:30:40.686470');
INSERT INTO guesses VALUES(2,14,7,'too low','2025-05-03 21:33:59.180982');
INSERT INTO guesses VALUES(3,15,7,'too low','2025-05-03 21:34:33.955460');
INSERT INTO guesses VALUES(4,16,7,'too low','2025-05-03 21:49:27.057823');
INSERT INTO guesses VALUES(5,16,8,'too low','2025-05-03 21:49:37.589031');
INSERT INTO guesses VALUES(6,16,9,'too low','2025-05-03 21:49:50.213304');
INSERT INTO guesses VALUES(7,16,9,'too low','2025-05-03 21:50:30.428348');
INSERT INTO guesses VALUES(8,17,35,'too low','2025-05-03 21:51:46.578981');
INSERT INTO guesses VALUES(9,18,7,'too high','2025-05-03 21:53:03.466215');
INSERT INTO guesses VALUES(10,18,4,'too high','2025-05-03 21:53:09.613420');
INSERT INTO guesses VALUES(11,18,2,'too low','2025-05-03 21:53:16.478188');
INSERT INTO guesses VALUES(12,19,7,'too high','2025-05-03 21:58:58.692378');
INSERT INTO guesses VALUES(13,19,3,'correct','2025-05-03 21:59:03.933976');
INSERT INTO guesses VALUES(14,20,7,'too high','2025-05-03 22:06:45.009261');
INSERT INTO guesses VALUES(15,20,3,'too high','2025-05-03 22:06:48.616077');
INSERT INTO guesses VALUES(16,20,2,'correct','2025-05-03 22:06:54.627074');
INSERT INTO guesses VALUES(17,21,7,'too high','2025-05-03 22:18:37.465713');
INSERT INTO guesses VALUES(18,21,3,'too low','2025-05-03 22:18:41.312853');
INSERT INTO guesses VALUES(19,21,5,'correct','2025-05-03 22:18:45.425299');
INSERT INTO guesses VALUES(20,22,35,'too high','2025-05-03 22:19:29.949177');
INSERT INTO guesses VALUES(21,22,25,'too high','2025-05-03 22:19:36.646779');
INSERT INTO guesses VALUES(22,22,20,'too high','2025-05-03 22:19:53.190055');
INSERT INTO guesses VALUES(23,22,10,'too low','2025-05-03 22:20:05.040759');
INSERT INTO guesses VALUES(24,22,15,'too low','2025-05-03 22:20:10.441951');
INSERT INTO guesses VALUES(25,22,18,'too high','2025-05-03 22:20:17.456346');
INSERT INTO guesses VALUES(26,22,17,'too high','2025-05-03 22:20:22.141568');
INSERT INTO guesses VALUES(27,23,25,'too low','2025-05-03 22:20:57.241763');
INSERT INTO guesses VALUES(28,23,35,'too low','2025-05-03 22:21:03.546107');
INSERT INTO guesses VALUES(29,23,45,'too high','2025-05-03 22:21:08.638329');
INSERT INTO guesses VALUES(30,23,40,'too low','2025-05-03 22:21:17.311507');
INSERT INTO guesses VALUES(31,23,42,'correct','2025-05-03 22:21:26.051315');
INSERT INTO guesses VALUES(32,24,50,'too high','2025-05-03 22:22:01.348826');
INSERT INTO guesses VALUES(33,24,30,'too low','2025-05-03 22:22:06.026256');
INSERT INTO guesses VALUES(34,24,40,'too low','2025-05-03 22:22:13.890249');
INSERT INTO guesses VALUES(35,24,45,'too low','2025-05-03 22:22:20.068023');
INSERT INTO guesses VALUES(36,24,47,'too low','2025-05-03 22:22:25.115758');
INSERT INTO guesses VALUES(37,24,49,'too high','2025-05-03 22:22:28.751991');
INSERT INTO guesses VALUES(38,24,48,'correct','2025-05-03 22:22:32.758312');
INSERT INTO guesses VALUES(39,25,50,'too low','2025-05-03 22:53:45.480753');
INSERT INTO guesses VALUES(40,25,70,'too low','2025-05-03 22:53:50.767400');
INSERT INTO guesses VALUES(41,25,85,'too high','2025-05-03 22:53:55.655212');
INSERT INTO guesses VALUES(42,25,75,'too low','2025-05-03 22:54:01.621847');
INSERT INTO guesses VALUES(43,25,80,'too low','2025-05-03 22:54:10.989164');
INSERT INTO guesses VALUES(44,25,83,'too high','2025-05-03 22:54:32.583385');
INSERT INTO guesses VALUES(45,25,82,'correct','2025-05-03 22:54:47.491147');
COMMIT;

WITH demo(title,category,synopsis,genre,platform,release_year,rating,duration_minutes,players) AS (VALUES
 ('Interestelar','MOVIE','Una tripulación viaja a través de un agujero de gusano para buscar un nuevo hogar para la humanidad.','Ciencia ficción, Drama','Cine, Streaming',2014,8.7,169,NULL),
 ('El viaje de Chihiro','MOVIE','Chihiro entra en un mundo de espíritus y debe encontrar valor para rescatar a sus padres.','Animación, Fantasía','Cine, Streaming',2001,8.6,125,NULL),
 ('Spider-Man: Into the Spider-Verse','MOVIE','Miles Morales descubre el multiverso y aprende a asumir su identidad como Spider-Man.','Animación, Acción','Cine, Streaming',2018,8.4,117,NULL),
 ('Dune: Parte Dos','MOVIE','Paul Atreides se une a los Fremen mientras enfrenta una decisión que puede cambiar el destino del universo.','Ciencia ficción, Aventura','Cine, Streaming',2024,8.5,166,NULL),
 ('The Matrix','MOVIE','Un programador descubre que su realidad es una simulación y se une a una rebelión.','Ciencia ficción, Acción','Cine, Streaming',1999,8.7,136,NULL),
 ('The Legend of Zelda: Breath of the Wild','GAME','Aventura de mundo abierto donde Link despierta para salvar Hyrule.','Aventura, Acción','Nintendo Switch',2017,9.5,NULL,'1'),
 ('Hades','GAME','Zagreo intenta escapar del inframundo en un juego de acción roguelike con narrativa progresiva.','Acción, Roguelike','PC, PlayStation, Xbox, Switch',2020,9.3,NULL,'1'),
 ('Minecraft','GAME','Juego de construcción y supervivencia en mundos generados por bloques, con modos individual y multijugador.','Sandbox, Supervivencia','PC, Consolas, Móvil',2011,9.0,NULL,'1-8+'),
 ('Baldur''s Gate 3','GAME','Aventura de rol basada en decisiones, exploración y combate táctico por turnos.','RPG, Fantasía','PC, PlayStation, Xbox',2023,9.6,NULL,'1-4'),
 ('Mario Kart 8 Deluxe','GAME','Carreras accesibles y competitivas con personajes de Nintendo y numerosos circuitos.','Carreras, Familiar','Nintendo Switch',2017,9.2,NULL,'1-12')
)
INSERT INTO catalog_items(title,category,synopsis,genre,platform,release_year,rating,duration_minutes,players)
SELECT d.* FROM demo d
WHERE NOT EXISTS (SELECT 1 FROM catalog_items c WHERE lower(c.title)=lower(d.title));

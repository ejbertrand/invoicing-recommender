
-- Helper Function for finding the ID of a service
DELIMITER EOF
CREATE FUNCTION srv_getid( name char(100) )
RETURNS INT
BEGIN
 DECLARE servID INT;
 SELECT id INTO servID FROM service WHERE service_type = name;
 RETURN servID;
END;
EOF

--  Helper Function for finding the name of a service
DELIMITER EOF
CREATE FUNCTION srv_getname( srvid INT )
RETURNS CHAR(100)
BEGIN
 DECLARE sname CHAR(100) DEFAULT '';
 SELECT service_type INTO sname FROM service WHERE id = srvid;
 RETURN sname;
END;
EOF
DELIMITER ;

 -- Stored Procedure for Adding a Sub-service
DELIMITER $
create procedure srv_addsub (sname varchar(100), pname varchar(100))
BEGIN
set @psrvid = (select srv_getid(pname));
IF @psrvid IS NOT NULL THEN
INSERT INTO service (service_type, parent_id, service_active) values (sname, @psrvid, 1);
END IF;
END$
DELIMITER ;

INSERT INTO service (service_type, parent_id, service_active) values ("Titles", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Bonds", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Paper Works", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Personal Insurance", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Commercial Insurance Personal/Business", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Business Insurance", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Home Insurance", NULL, 1);
INSERT INTO service (service_type, parent_id, service_active) values ("Auto Auction", NULL, 1);

call srv_addsub("Title/Sticker/Plates", "Titles");
call srv_addsub("Title Only", "Titles");
call srv_addsub("Sticker/Plates", "Titles");
call srv_addsub("Sticker Only", "Titles");
call srv_addsub("Sticker on line", "Titles");
call srv_addsub("Transfer Notification", "Titles");
call srv_addsub("Change Address", "Titles");
call srv_addsub("Bond Only", "Bonds");
call srv_addsub("Bond/Title/Sticker/Plates/Blue Title", "Bonds");
call srv_addsub("Bond/Title/Sticker/Plates/Salvage Title", "Bonds");
call srv_addsub("Bond/Title Only", "Bonds");
call srv_addsub("Dealer Bond", "Bonds");
call srv_addsub("Other Bonds", "Bonds");
call srv_addsub("General Notary Services", "Paper Works");
call srv_addsub("Gift Transfer", "Paper Works");
call srv_addsub("New Policy Auto", "Personal Insurance");
call srv_addsub("Endorsements", "Personal Insurance");
call srv_addsub("Change Company Same Agent", "Personal Insurance");
call srv_addsub("New Policy", "Commercial Insurance Personal/Business");
call srv_addsub("Endorsements", "Commercial Insurance Personal/Business");
call srv_addsub("New Policy", "Business Insurance");
call srv_addsub("Endorsements", "Business Insurance");
call srv_addsub("New Policy", "Home Insurance");
call srv_addsub("Endorsements", "Home Insurance");
call srv_addsub("Fee Auto Auction", "Auto Auction");
call srv_addsub("Title Re-Sale", "Auto Auction");
call srv_addsub("Title Change", "Auto Auction");
call srv_addsub("Specific Agent Tag", "Auto Auction");


-- Query for transactions
SELECT a.date, b.user_name, c.service_type, d.service_type, e.payment_type, a.client_name, a.total, a.comments
FROM transaction a
INNER JOIN user b ON a.user_id = b.id
INNER JOIN service c ON a.service_id = c.id
INNER JOIN service d ON a.subservice_id = d.id
INNER JOIN payment e ON a.payment_id = e.id

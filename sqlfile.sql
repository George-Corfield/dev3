INSERT INTO 
users(EMAIL,USERNAME,PWORD,OrgID) 
VALUES (email,username,pword,0)

SELECT * FROM users
WHERE USERNAME=username

SELECT users.UserID, users.USERNAME
FROM users
WHERE OrgID=orgID AND UserID=userID

SELECT * 
FROM rooms
INNER JOIN organisation
ON rooms.RoomID = Rid AND organisation.OrgID = OrgID

INSERT INTO messages(MESSAGES, ConnectionID, Date, Time)
VALUES (message,connectionID,date, time)

SELECT messages.MessageID, messages.Message, messages.Date, messages.Time, 
connections.UserID, connections.RoomID, users.USERNAME, rooms.ROOM 
FROM messages 
INNER JOIN connections 
ON messages.ConnectionID=connectionID AND connections.ConnectionID=connectionID 
INNER JOIN users 
ON connections.UserID=users.UserID AND connections.ConnectionID=connectionID
INNER JOIN rooms
ON rooms.RoomID = connections.RoomID


SELECT EXISTS 
(SELECT 1 
 FROM organisation 
 WHERE OrgName=orgName)

UPDATE users 
SET OrgID=orgID, RoleID=roleID
WHERE UserID=userID

UPDATE users
SET StatusID = statusID
WHERE UserID = userID

SELECT COUNT(*) 
FROM connections
WHERE RoomID=rid

SELECT connections.UserID, users.USERNAME, status.STATUS
FROM connections
INNER JOIN users
ON connections.RoomID = ? AND connections.UserID=users.UserID
INNER JOIN status
ON users.StatusID = status.StatusID
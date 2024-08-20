--@block
-- Accounts -- 
ALTER TABLE Accounts
ADD PRIMARY KEY (AccountID)

--@block
-- Leads --
ALTER TABLE Leads
ADD PRIMARY KEY (LeadID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
ADD FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)

--@block
-- Clients --
ALTER TABLE Clients
ADD PRIMARY KEY (ClientID),
ADD UNIQUE (License);

--@block
-- Users --
ALTER TABLE Users
ADD PRIMARY KEY (UserID),
MODIFY UserID INT AUTO_INCREMENT,
ADD UNIQUE (Email);

--@block
DELETE FROM Opportunities

--@block
-- Opportunities --
ALTER TABLE Opportunities
ADD PRIMARY KEY (OpportunityID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
MODIFY OpportunityID INT AUTO_INCREMENT;


--@block
-- Orders --
ALTER TABLE Orders
ADD PRIMARY KEY (OrderID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID);

--@block
ALTER TABLE OrderDetails
ADD PRIMARY KEY (OrderDetailID),
ADD FOREIGN KEY (OrderID) REFERENCES Orders(OrderID);

--@block
ALTER TABLE SupportTickets
ADD PRIMARY KEY (TicketID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
ADD FOREIGN KEY (ContactID) REFERENCES Contacts(ContactID)


--@block
INSERT INTO Clients VALUES (100100, 'Southern California Edison', '9b2a012a1a1c425a8c86', '/images/9b2a012a1a1c425a8c86.png', 1, 1)

--@block
INSERT INTO Clients VALUES(100000, 'ERP Center, Inc.', '3a95d70c85864ab99603', '/images/3a95d70c85864ab99603.png', 1, 1)

--@block
ALTER TABLE Leads
ADD PRIMARY KEY (LeadID)

--@block
UPDATE Users
SET FirstName = 'Haris', LastName = 'Saif'
WHERE (Email='haris.saif@erp-center.com')

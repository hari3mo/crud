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
MODIFY ClientID INT AUTO_INCREMENT,
ADD UNIQUE (License);

--@block
-- Users --
ALTER TABLE Users
ADD PRIMARY KEY (UserID),
MODIFY UserID INT AUTO_INCREMENT,
ADD UNIQUE (Email);

--@block
DELETE FROM Users

--@block
-- Opportunities --
ALTER TABLE Opportunities
ADD PRIMARY KEY (OpportunityID)


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
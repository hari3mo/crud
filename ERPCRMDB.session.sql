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
AUTO_INCREMENT=0,
ADD UNIQUE (License);

--@block
-- Users --
ALTER TABLE Users
ADD PRIMARY KEY (UserID),
MODIFY UserID INT AUTO_INCREMENT,
AUTO_INCREMENT=0,
ADD UNIQUE (Email);

--@block
DELETE FROM Opportunities

--@block
-- Opportunities --
ALTER TABLE Opportunities
ADD PRIMARY KEY (OpportunityID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
MODIFY OpportunityID INT AUTO_INCREMENT,
AUTO_INCREMENT=0;


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


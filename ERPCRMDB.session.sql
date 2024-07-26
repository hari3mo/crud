--@block
ALTER TABLE Accounts
ADD PRIMARY KEY (AccountID)

--@block
ALTER TABLE Leads
ADD PRIMARY KEY (LeadID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)

--@block
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
--ALTER TABLE Accounts AUTO_INCREMENT=1000;
--ALTER TABLE Leads AUTO_INCREMENT=100000;

--@block


--@block
DELETE FROM Accounts


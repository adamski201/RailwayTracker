DROP TABLE Incidents;
DROP TABLE OperatorSubscriptions;
DROP TABLE StationSubscriptions;
DROP TABLE Users;
DROP TABLE Arrivals;
DROP TABLE Cancellations;
DROP TABLE CancellationTypes;
DROP TABLE Services;
DROP TABLE Operators;
DROP TABLE Stations;


CREATE TABLE Stations(
    StationID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    CRSCode varchar(3) UNIQUE NOT NULL,
    StationName varchar(60) NOT NULL
);

CREATE TABLE Operators(
    OperatorID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    OperatorName varchar(60) NOT NULL,
    OperatorCode varchar(2) UNIQUE
);

CREATE TABLE Services(
    ServiceID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ServiceUID varchar(6) UNIQUE NOT NULL,
    OperatorID INT REFERENCES Operators(OperatorID)
);

CREATE TABLE CancellationTypes(
    CancellationTypeID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    CancellationCode varchar(2) UNIQUE NOT NULL,
    Description text
);

CREATE TABLE Cancellations(
    CancellationID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ScheduledArrival timestamp NOT NULL,
    CancellationTypeID INT REFERENCES CancellationTypes(CancellationTypeID),
    StationID INT REFERENCES Stations(StationID),
    ServiceID INT REFERENCES Services(ServiceID)
);

CREATE TABLE Arrivals(
    ArrivalID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ScheduledArrival timestamp NOT NULL,
    ActualArrival timestamp NOT NULL,
    StationID INT REFERENCES Stations(StationID),
    ServiceID INT REFERENCES Services(ServiceID)
);

CREATE TABLE Users(
    UserID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    FirstName varchar(30) NOT NULL,
    LastName varchar(60) NOT NULL,
    PhoneNumber varchar(20),
    Email varchar
);

CREATE TABLE StationSubscriptions(
    StationSubscriptionID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    IsActive BOOLEAN NOT NULL,
    UserID INT REFERENCES Users(UserID),
    StationID INT REFERENCES Stations(StationID)
);

CREATE TABLE OperatorSubscriptions(
    OperatorSubscriptionID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    IsActive BOOLEAN NOT NULL,
    UserID INT REFERENCES Users(UserID),
    OperatorID INT REFERENCES Operators(OperatorID)
);

CREATE TABLE Incidents(
    IncidentRecordID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OperatorID INT REFERENCES Operators(OperatorID),
    CreationDate timestamp NOT NULL, 
    Description text,
    Summary text, 
    StartDate timestamp NOT NULL,
    EndDate timestamp,
    InfoLink text,
    AffectedRoutes text,
    Planned BOOLEAN NOT NULL,
    IncidentNumber varchar(32) UNIQUE NOT NULL,
    LastUpdated timestamp
);
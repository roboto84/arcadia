
CREATE TABLE ITEMS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    time_stamp TEXT NOT NULL,
    data TEXT NOT NULL,
    data_type TEXT NOT NULL,
    tags TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT 'None',
    description TEXT NOT NULL DEFAULT 'None',
    image TEXT NOT NULL DEFAULT 'None'
);

-- Databse schema, use on new instance creation

PRAGMA foreign_keys = ON;

CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    fullname TEXT NOT NULL,
    qualification TEXT,
    dob DATE NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user', 'faculty')) NOT NULL DEFAULT 'user' 
);

CREATE TABLE Api (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    token TEXT UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE Courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE Assignment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    duration TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE
);

-- CREATE TABLE Questions (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     quiz_id INTEGER NOT NULL,
--     qstatement TEXT NOT NULL,
--     opt1 TEXT NOT NULL,
--     opt2 TEXT NOT NULL,
--     opt3 TEXT,
--     opt4 TEXT,
--     copt INTEGER NOT NULL, 
--     FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
-- );

-- CREATE TABLE Scores (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     quiz_id INTEGER NOT NULL,
--     user_id INTEGER NOT NULL,
--     time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
--     report TEXT NOT NULL,
--     marks INTEGER NOT NULL,
--     ratio TEXT NOT NULL,
--     FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
-- );


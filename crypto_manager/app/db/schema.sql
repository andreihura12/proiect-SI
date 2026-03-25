CREATE TABLE IF NOT EXISTS Files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    status TEXT DEFAULT 'Necriptat',
    file_type TEXT,
    size_bytes INTEGER,
    hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Algorithms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    key_size INTEGER,
    mode TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_id INTEGER NOT NULL,
    key_name TEXT NOT NULL,
    key_type TEXT NOT NULL,
    key_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (algorithm_id) REFERENCES Algorithms(id)
);

CREATE TABLE IF NOT EXISTS Frameworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT
);

CREATE TABLE IF NOT EXISTS Operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    algorithm_id INTEGER NOT NULL,
    framework_id INTEGER NOT NULL,
    key_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,
    input_path TEXT NOT NULL,
    output_path TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES Files(id),
    FOREIGN KEY (algorithm_id) REFERENCES Algorithms(id),
    FOREIGN KEY (framework_id) REFERENCES Frameworks(id),
    FOREIGN KEY (key_id) REFERENCES Keys(id)
);

CREATE TABLE IF NOT EXISTS Performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    memory INTEGER,
    execution_time INTEGER,
    FOREIGN KEY (operation_id) REFERENCES Operations(id)
);
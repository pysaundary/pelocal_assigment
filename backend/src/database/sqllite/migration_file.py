MIGRATION_SCRIPT =[ """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL UNIQUE,
    slug       TEXT    NOT NULL UNIQUE,
    profile    TEXT    NOT NULL DEFAULT '{}'
      CHECK (json_valid(profile))
);

CREATE INDEX IF NOT EXISTS idx_users_email
  ON users ( json_extract(profile, '$.email') );

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    payload     TEXT    NOT NULL
      CHECK (json_valid(payload)),
    created_by  INTEGER NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by)
      REFERENCES users (id)
      ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_created_by
  ON tasks (created_by);

CREATE INDEX IF NOT EXISTS idx_tasks_priority
  ON tasks ( json_extract(payload, '$.priority') );
"""
]
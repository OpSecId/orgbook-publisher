import sqlite3
import json

class SQLite:
    def __init__(self):
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()
        
    def provision(self):
        sql = """
DROP TABLE IF EXISTS invitations;

CREATE TABLE invitations (
    id TEXT PRIMARY KEY NOT NULL,
    data TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
);
"""
        self.connection.executescript(sql)
        self.connection.commit()
        self.connection.close()
        
    def new_invitation(self, invitation_id, invitation):
        self.cursor.execute("INSERT INTO invitations (id, invitation) VALUES (?, ?)",
            (invitation_id, json.dumps(invitation))
        )
        self.connection.commit()
        self.connection.close()
        
    def get_invitation(self, invitation_id):
        self.connection.row_factory = sqlite3.Row
        invitation = self.connection.execute('SELECT FROM invitations WHERE id = ?', (invitation_id,)).fetchone()
        if invitation is None:
            pass
        invitation = self.connection.execute('DELETE FROM invitations WHERE id = ?', (invitation_id,))
        self.connection.commit()
        self.connection.close()
        return json.loads(invitation.data)
        
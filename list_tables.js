const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("SELECT name FROM sqlite_master WHERE type='table'", function(err, tables) {
    console.log('tables:', tables.map(function(t){ return t.name; }).join(', '));
    db.close();
  });
});
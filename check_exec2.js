const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("PRAGMA table_info(execution_entity)", function(err, cols) {
    console.log('columns:', cols.map(function(c){ return c.name; }).join(', '));
    db.all("SELECT id, workflowId, status, stoppedAt FROM execution_entity ORDER BY id DESC LIMIT 5", function(err, rows) {
      if (err) { console.error(err.message); db.close(); return; }
      console.log(JSON.stringify(rows, null, 2));
      db.close();
    });
  });
});
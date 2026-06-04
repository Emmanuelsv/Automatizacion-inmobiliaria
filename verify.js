const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("SELECT id, versionId, active FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, rows) {
    console.log('workflow entity:', JSON.stringify(rows));
  });
  db.all("SELECT * FROM workflow_statistics", function(err, rows) {
    console.log('stats rows:', rows ? rows.length : 0);
    db.close();
  });
});
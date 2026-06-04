const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("SELECT * FROM workflow_published_version", function(err, rows) {
    console.log("workflow_published_version:", JSON.stringify(rows));
  });
  db.get("SELECT id, name, active, versionId FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    console.log("workflow_entity:", JSON.stringify(row));
    db.close();
  });
});
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("SELECT id, workflowId, status, stoppedAt, data FROM execution_entity ORDER BY id DESC LIMIT 3", function(err, rows) {
    if (err) { console.error(err.message); db.close(); return; }
    rows.forEach(function(r) {
      var d = JSON.parse(r.data || '{}');
      console.log('--- exec', r.id, '---');
      console.log('status:', r.status);
      console.log('stoppedAt:', r.stoppedAt);
      if (d.lastNodeExecuted) console.log('lastNode:', d.lastNodeExecuted);
      if (d.errorMessage) console.log('error:', d.errorMessage);
    });
    db.close();
  });
});
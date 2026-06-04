const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READWRITE, function(err) {
  if (err) { console.error(err.message); return; }

  db.get("SELECT nodes, versionId FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    if (err) { console.error(err.message); db.close(); return; }
    console.log('Current versionId:', row.versionId);
    var nodes = JSON.parse(row.nodes);
    var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
    if (extraer) console.log('Extraer code (first 80):', extraer.parameters.jsCode.substring(0, 80));

    var versionId = row.versionId;
    var now = new Date().toISOString();

    // Insert or replace into workflow_published_version
    db.run(
      "INSERT OR REPLACE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt) VALUES (?, ?, ?, ?)",
      ['wS1VtPLDqJsZwu8y', versionId, now, now],
      function(err2) {
        if (err2) { console.error('insert error:', err2.message); db.close(); return; }
        console.log('workflow_published_version written, changes:', this.changes);

        // Checkpoint WAL
        db.run("PRAGMA wal_checkpoint(FULL)", function(err3) {
          if (err3) console.error('checkpoint error:', err3.message);
          else console.log('WAL checkpoint done');
          db.close(function() { console.log('Done - restart n8n to apply.'); });
        });
      }
    );
  });
});
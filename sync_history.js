// Syncs workflow_entity.nodes -> workflow_history[versionId].nodes and checkpoints WAL
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READWRITE, function(err) {
  if (err) { console.error('open:', err.message); return; }
  
  db.get("SELECT nodes, versionId FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    if (err) { console.error('get entity:', err.message); db.close(); return; }
    
    var currentVersionId = row.versionId;
    var currentNodes = row.nodes;
    
    var nodes = JSON.parse(currentNodes);
    var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
    console.log('versionId:', currentVersionId);
    console.log('Current code (first 70):', extraer.parameters.jsCode.substring(0, 70));
    
    // Update workflow_history for this versionId with current nodes
    db.run("UPDATE workflow_history SET nodes=? WHERE versionId=?", [currentNodes, currentVersionId], function(err) {
      if (err) { console.error('update history:', err.message); db.close(); return; }
      if (this.changes === 0) {
        console.log('No history row found - versionId may be new. Checking...');
        // History row might not exist yet if PATCH just created it
        db.run("INSERT OR IGNORE INTO workflow_history (versionId, workflowId, nodes, connections, createdAt, updatedAt, authors, name, autosaved, description) SELECT ?, 'wS1VtPLDqJsZwu8y', ?, connections, datetime('now'), datetime('now'), '[]', name, 0, '' FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", [currentVersionId, currentNodes], function(err2) {
          if (err2) { console.error('insert:', err2.message); db.close(); return; }
          console.log('Inserted history row, changes:', this.changes);
          checkpoint(db);
        });
      } else {
        console.log('Updated workflow_history rows:', this.changes);
        checkpoint(db);
      }
    });
  });
});

function checkpoint(db) {
  db.run("PRAGMA wal_checkpoint(FULL)", function(err) {
    if (err) console.error('checkpoint:', err.message);
    else console.log('WAL checkpoint done');
    db.close(function() { console.log('DB closed. Ready to restart.'); });
  });
}
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  // Check current versionId in workflow_entity
  db.get("SELECT versionId FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    console.log('workflow_entity versionId:', row.versionId);
    
    // Get the nodes from workflow_history for that versionId
    db.get("SELECT nodes FROM workflow_history WHERE versionId=?", [row.versionId], function(err2, histRow) {
      if (err2) { console.error('history error:', err2.message); db.close(); return; }
      if (!histRow) { console.log('No history row for this versionId'); db.close(); return; }
      var nodes = JSON.parse(histRow.nodes);
      var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
      if (extraer) {
        console.log('history versionId code (first 80):', extraer.parameters.jsCode.substring(0, 80));
      }
      db.close();
    });
  });
});
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("SELECT executionId, workflowVersionId FROM execution_data WHERE executionId >= 616", function(err, rows) {
    console.log(JSON.stringify(rows, null, 2));
    
    // Also check what code is in workflow_history for each versionId
    rows.forEach(function(r) {
      if (!r.workflowVersionId) return;
      db.get("SELECT nodes FROM workflow_history WHERE versionId=?", [r.workflowVersionId], function(err2, hist) {
        if (!hist) { console.log('exec', r.executionId, 'versionId', r.workflowVersionId, '-> NO history row'); return; }
        var nodes = JSON.parse(hist.nodes);
        var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
        console.log('exec', r.executionId, 'versionId', r.workflowVersionId, '-> code:', extraer ? extraer.parameters.jsCode.substring(0, 60) : 'NOT FOUND');
      });
    });
    setTimeout(function(){ db.close(); }, 500);
  });
});
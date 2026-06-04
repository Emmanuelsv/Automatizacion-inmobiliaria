const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT workflowVersionId FROM execution_data WHERE executionId=620", function(err, row) {
    console.log('execution 620 versionId:', row ? row.workflowVersionId : 'none');
    if (row && row.workflowVersionId) {
      db.get("SELECT nodes FROM workflow_history WHERE versionId=?", [row.workflowVersionId], function(err2, hist) {
        if (!hist) { console.log('no history'); db.close(); return; }
        var nodes = JSON.parse(hist.nodes);
        var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
        console.log('history code:', extraer ? extraer.parameters.jsCode.substring(0, 100) : 'NOT FOUND');
        db.close();
      });
    } else {
      db.close();
    }
  });
});
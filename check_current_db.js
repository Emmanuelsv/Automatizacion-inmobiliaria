const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT nodes, versionId FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    if (err) { console.error(err.message); db.close(); return; }
    console.log('versionId:', row.versionId);
    var nodes = JSON.parse(row.nodes);
    var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
    console.log('nodes Extraer code:', extraer.parameters.jsCode.substring(0, 100));
    db.close();
  });
});
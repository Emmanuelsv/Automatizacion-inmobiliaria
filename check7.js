const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.all("PRAGMA table_info(workflow_published_version)", function(err, cols) {
    console.log('wpv cols:', cols.map(function(c){ return c.name; }).join(', '));
  });
  db.all("SELECT workflowId FROM workflow_published_version", function(err, rows) {
    console.log('wpv rows:', JSON.stringify(rows));
  });
  // Also re-verify current nodes code
  db.get("SELECT nodes FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    var nodes = JSON.parse(row.nodes);
    var extraer = nodes.find(function(n){ return n.name === 'Extraer texto'; });
    console.log('current nodes code:', extraer.parameters.jsCode.substring(0, 80));
    db.close();
  });
});
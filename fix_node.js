const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READWRITE, function(err) {
  if (err) { console.error('open error:', err.message); return; }
  
  db.get('SELECT nodes FROM workflow_entity WHERE id=?', ['wS1VtPLDqJsZwu8y'], function(err, row) {
    if (err) { console.error('select error:', err.message); return; }
    
    var nodes = JSON.parse(row.nodes);
    var idx = nodes.findIndex(function(n) { return n.name === 'Extraer texto'; });
    
    var newCode = "const msg = $json.body.messages[0];\nconst text = msg.text?.body || msg.caption || '';\nconst sender = msg.from || '';\nconst groupId = msg.chat_id || '';\nconst pushName = msg.from_name || '';\n\nreturn [{ json: { text, sender, groupId, pushName } }];";
    
    nodes[idx].parameters.jsCode = newCode;
    
    var updatedNodes = JSON.stringify(nodes);
    db.run('UPDATE workflow_entity SET nodes=? WHERE id=?', [updatedNodes, 'wS1VtPLDqJsZwu8y'], function(err) {
      if (err) { console.error('update error:', err.message); return; }
      console.log('Updated rows:', this.changes);
      db.close();
    });
  });
});
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READWRITE, function(err) {
  if (err) { console.error('open:', err.message); return; }
  
  db.get("SELECT nodes, versionId FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
    if (err) { console.error('get:', err.message); db.close(); return; }
    
    var currentVersionId = row.versionId;
    console.log('Current versionId:', currentVersionId);
    
    var nodes = JSON.parse(row.nodes);
    var extraerIdx = nodes.findIndex(function(n){ return n.name === 'Extraer texto'; });
    
    var correctCode = "const msg = $json.body.messages[0];\nconst text = msg.text?.body || msg.caption || '';\nconst sender = msg.from || '';\nconst groupId = msg.chat_id || '';\nconst pushName = msg.from_name || '';\n\nreturn [{ json: { text, sender, groupId, pushName } }];";
    
    nodes[extraerIdx].parameters.jsCode = correctCode;
    var nodesStr = JSON.stringify(nodes);
    
    // Step 1: Update workflow_entity
    db.run("UPDATE workflow_entity SET nodes=? WHERE id='wS1VtPLDqJsZwu8y'", [nodesStr], function(err) {
      if (err) { console.error('update entity:', err.message); db.close(); return; }
      console.log('Updated workflow_entity, rows:', this.changes);
      
      // Step 2: Update workflow_history for current versionId
      db.get("SELECT nodes FROM workflow_history WHERE versionId=?", [currentVersionId], function(err, histRow) {
        if (err || !histRow) {
          console.log('No history row for versionId', currentVersionId, '- will create one');
          // Insert if not exists
          db.run("INSERT OR REPLACE INTO workflow_history (versionId, workflowId, nodes, connections, createdAt, updatedAt, authors, name) SELECT ?, 'wS1VtPLDqJsZwu8y', ?, connections, datetime('now'), datetime('now'), '[]', name FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'",
            [currentVersionId, nodesStr], function(err2) {
              if (err2) console.error('insert history:', err2.message);
              else console.log('Inserted/replaced workflow_history');
              checkpoint(db);
            });
        } else {
          var histNodes = JSON.parse(histRow.nodes);
          var histExtraerIdx = histNodes.findIndex(function(n){ return n.name === 'Extraer texto'; });
          if (histExtraerIdx >= 0) histNodes[histExtraerIdx].parameters.jsCode = correctCode;
          var histNodesStr = JSON.stringify(histNodes);
          
          db.run("UPDATE workflow_history SET nodes=? WHERE versionId=?", [histNodesStr, currentVersionId], function(err2) {
            if (err2) { console.error('update history:', err2.message); db.close(); return; }
            console.log('Updated workflow_history, rows:', this.changes);
            console.log('History code:', histNodes[histExtraerIdx].parameters.jsCode.substring(0, 60));
            checkpoint(db);
          });
        }
      });
    });
  });
});

function checkpoint(db) {
  db.run("PRAGMA wal_checkpoint(FULL)", function(err) {
    if (err) console.error('checkpoint:', err.message);
    else console.log('WAL checkpoint done');
    db.close(function() { console.log('DB closed'); });
  });
}
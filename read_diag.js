const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  // Get latest execution
  db.get("SELECT id FROM execution_entity ORDER BY id DESC LIMIT 1", function(err, row) {
    if (!row) { console.log('no exec'); db.close(); return; }
    var execId = row.id;
    console.log('Latest execution ID:', execId);
    
    db.get("SELECT data FROM execution_data WHERE executionId=?", [execId], function(err, drow) {
      if (!drow || !drow.data) { console.log('no data'); db.close(); return; }
      var raw = drow.data;
      var buf;
      if (typeof raw === 'string') { buf = Buffer.from(raw, 'utf8'); }
      else if (Buffer.isBuffer(raw)) { buf = raw; }
      else { var buf2 = Buffer.alloc(Object.keys(raw).length); Object.keys(raw).forEach(function(k){ buf2[parseInt(k)] = raw[k]; }); buf = buf2; }
      
      var str = buf.toString('utf8');
      // Find the DIAG error message
      var diagIdx = str.indexOf('DIAG:');
      if (diagIdx >= 0) {
        console.log('DIAG found:', str.substring(diagIdx, diagIdx + 500));
      } else {
        console.log('No DIAG found');
        // Look for error
        var errIdx = str.indexOf('"message"');
        if (errIdx >= 0) console.log('Error context:', str.substring(errIdx, errIdx + 200));
      }
      db.close();
    });
  });
});
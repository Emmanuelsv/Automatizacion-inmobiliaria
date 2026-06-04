const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data FROM execution_data WHERE executionId=621", function(err, row) {
    if (!row || !row.data) { console.log('no data'); db.close(); return; }
    var raw = row.data;
    var buf = Buffer.isBuffer(raw) ? raw : Buffer.from(Object.values(raw));
    var str = buf.toString('utf8');
    
    // Find jsCode in the packed data
    var jsIdx = str.indexOf('"jsCode"');
    if (jsIdx >= 0) {
      // Find the next string value after jsCode key
      var start = str.indexOf(',', jsIdx) + 1;
      var codeRef = str.substring(jsIdx - 5, jsIdx + 200);
      console.log('Context around jsCode:', codeRef);
    }
    
    // Also find the code string itself (look for "const msg" or "// Accedemos")
    var newCodeIdx = str.indexOf('const msg = ');
    var oldCodeIdx = str.indexOf('chats_updates');
    console.log('NEW code found at:', newCodeIdx, '| OLD code found at:', oldCodeIdx);
    
    db.close();
  });
});
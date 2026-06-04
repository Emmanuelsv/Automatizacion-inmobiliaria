const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data FROM execution_data WHERE executionId=620", function(err, row) {
    if (!row || !row.data) { console.log('no data'); db.close(); return; }
    var raw = row.data;
    var buf;
    if (typeof raw === 'string') { buf = Buffer.from(raw, 'utf8'); }
    else if (Buffer.isBuffer(raw)) { buf = raw; }
    else { buf = Buffer.from(Object.values(raw)); }
    
    var str = buf.toString('utf8');
    // Print the full string to understand structure
    console.log('FULL DATA:', str);
    db.close();
  });
});
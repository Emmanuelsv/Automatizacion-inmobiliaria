const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const zlib = require('zlib');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data FROM execution_data WHERE executionId=619", function(err, row) {
    if (err) { console.error(err.message); db.close(); return; }
    if (!row || !row.data) { console.log('no data'); db.close(); return; }
    
    var raw = row.data;
    var buf;
    if (typeof raw === 'string') {
      buf = Buffer.from(raw, 'utf8');
    } else if (Buffer.isBuffer(raw)) {
      buf = raw;
    } else {
      buf = Buffer.from(Object.values(raw));
    }
    
    console.log('Buffer length:', buf.length, 'first bytes (hex):', buf.slice(0, 8).toString('hex'));
    
    // Try gzip first
    if (buf[0] === 0x1f && buf[1] === 0x8b) {
      zlib.gunzip(buf, function(e, result) {
        if (e) { console.log('gunzip failed:', e.message); db.close(); return; }
        var str = result.toString('utf8');
        console.log('gunzip success, first 1000 chars:', str.substring(0, 1000));
        db.close();
      });
    } else {
      // Try as UTF-8 directly
      var str = buf.toString('utf8');
      console.log('raw utf8 first 500:', str.substring(0, 500));
      db.close();
    }
  });
});
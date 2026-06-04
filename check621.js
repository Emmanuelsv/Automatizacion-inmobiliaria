const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const zlib = require('zlib');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT workflowVersionId FROM execution_data WHERE executionId=621", function(err, row) {
    console.log('exec 621 versionId:', row ? row.workflowVersionId : 'none');
    
    db.get("SELECT data FROM execution_data WHERE executionId=621", function(err, drow) {
      if (!drow || !drow.data) { console.log('no data'); db.close(); return; }
      var raw = drow.data;
      var buf = Buffer.isBuffer(raw) ? raw : Buffer.from(Object.values(raw));
      
      // Check if it's gzipped
      if (buf[0] === 0x1f && buf[1] === 0x8b) {
        zlib.gunzip(buf, function(e, result) {
          if (e) { console.log('gunzip failed:', e.message); }
          else {
            var str = result.toString('utf8');
            var newCodeIdx = str.indexOf('const msg = ');
            var oldCodeIdx = str.indexOf('chats_updates');
            console.log('Gzipped - NEW code at:', newCodeIdx, '| OLD code at:', oldCodeIdx);
            if (newCodeIdx >= 0) console.log('new code context:', str.substring(newCodeIdx, newCodeIdx + 80));
            if (oldCodeIdx >= 0) console.log('old code context:', str.substring(oldCodeIdx - 20, oldCodeIdx + 80));
          }
          db.close();
        });
      } else {
        var str = buf.toString('utf8');
        console.log('Not gzipped, length:', str.length);
        console.log('First 200:', str.substring(0, 200));
        var newCodeIdx = str.indexOf('const msg = ');
        var oldCodeIdx = str.indexOf('chats_updates');
        console.log('NEW code at:', newCodeIdx, '| OLD code at:', oldCodeIdx);
        db.close();
      }
    });
  });
});
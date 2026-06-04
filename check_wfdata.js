const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const zlib = require('zlib');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT workflowData FROM execution_data WHERE executionId=619", function(err, row) {
    if (err) { console.error(err.message); db.close(); return; }
    if (!row || !row.workflowData) { console.log('no workflowData'); db.close(); return; }
    
    var raw = row.workflowData;
    // It might be stored as a Buffer or string
    if (typeof raw === 'string') {
      try {
        var parsed = JSON.parse(raw);
        var extraer = parsed.nodes && parsed.nodes.find(function(n){ return n.name === 'Extraer texto'; });
        if (extraer) console.log('workflowData Extraer code:', extraer.parameters.jsCode.substring(0, 80));
      } catch(e) {
        console.log('workflowData first 200:', raw.substring(0, 200));
      }
    } else {
      // It's a Buffer - try to decompress
      var buf = Buffer.from(Object.values(raw));
      console.log('Buffer length:', buf.length, 'first bytes:', buf.slice(0, 4).toString('hex'));
      // Check if gzipped
      if (buf[0] === 0x1f && buf[1] === 0x8b) {
        zlib.gunzip(buf, function(err, result) {
          if (err) { console.log('gunzip failed:', err.message); db.close(); return; }
          var str = result.toString('utf8');
          try {
            var parsed = JSON.parse(str);
            var extraer = parsed.nodes && parsed.nodes.find(function(n){ return n.name === 'Extraer texto'; });
            if (extraer) console.log('workflowData Extraer code:', extraer.parameters.jsCode.substring(0, 80));
            else console.log('workflowData keys:', Object.keys(parsed).join(', '));
          } catch(e) {
            console.log('JSON parse err:', e.message, str.substring(0, 200));
          }
          db.close();
        });
      } else {
        var str = buf.toString('utf8');
        console.log('raw string first 200:', str.substring(0, 200));
        db.close();
      }
    }
  });
});
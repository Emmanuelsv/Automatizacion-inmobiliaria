const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data FROM execution_data WHERE executionId=619", function(err, row) {
    var raw = row.data;
    // raw might be a Buffer stored as a Blob
    var str;
    if (typeof raw === 'string') {
      str = raw;
    } else if (Buffer.isBuffer(raw)) {
      str = raw.toString('utf8');
    } else {
      // It's an object with numeric keys - it's a buffer
      var buf = Buffer.alloc(Object.keys(raw).length);
      Object.keys(raw).forEach(function(k) { buf[parseInt(k)] = raw[k]; });
      str = buf.toString('utf8');
    }
    // n8n stores execution data as a "packed" format
    // The str starts with [{ "version":1,... } which is a packed JSON
    // Let's find the Webhook input data by looking for "body" in the string
    var bodyIdx = str.indexOf('"body"');
    if (bodyIdx >= 0) {
      console.log('Found "body" at index', bodyIdx);
      console.log('Context around body:', str.substring(Math.max(0, bodyIdx-50), bodyIdx+300));
    } else {
      console.log('No "body" found in data');
      console.log('First 200:', str.substring(0, 200));
    }
    db.close();
  });
});
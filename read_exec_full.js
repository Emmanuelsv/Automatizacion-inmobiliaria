const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data FROM execution_data WHERE executionId=619", function(err, row) {
    var raw = row.data;
    var buf = Buffer.isBuffer(raw) ? raw : Buffer.from(Object.values(raw));
    var str = buf.toString('utf8');
    // Parse the compressed format
    var arr = JSON.parse(str);
    
    // arr[0] has refs like "version", "startData", "resultData", "executionData"
    // arr[1..] have the actual data indexed by string
    // Let's find the Webhook runData
    var full = str;
    // Find Webhook runData
    var webhookIdx = full.indexOf('"Webhook"');
    console.log('Full string around Webhook (chars 3800-4825):');
    console.log(full.substring(3800, full.length));
    db.close();
  });
});
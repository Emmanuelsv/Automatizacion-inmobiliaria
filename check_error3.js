const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data FROM execution_data WHERE executionId=616", function(err, row) {
    if (err) { console.error(err.message); db.close(); return; }
    if (!row) { console.log('no row'); db.close(); return; }
    try {
      var d = JSON.parse(row.data);
      if (d.resultData) {
        console.log('lastNode:', d.resultData.lastNodeExecuted);
        if (d.resultData.error) {
          console.log('error message:', d.resultData.error.message);
          console.log('error description:', d.resultData.error.description);
        }
      }
    } catch(e) {
      console.log('parse error:', e.message);
      console.log('raw (first 500):', String(row.data).substring(0, 500));
    }
    db.close();
  });
});
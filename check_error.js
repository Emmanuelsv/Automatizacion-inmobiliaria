const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  // Check execution_data for error details on execution 616
  db.get("SELECT executionId, workflowData FROM execution_data WHERE executionId=616", function(err, row) {
    if (err) { console.error('exec_data error:', err.message); }
    else if (row) {
      var wd = JSON.parse(row.workflowData || '{}');
      // Find the last executed node and error
      if (wd.resultData) {
        console.log('lastNode:', wd.resultData.lastNodeExecuted);
        if (wd.resultData.error) console.log('error:', JSON.stringify(wd.resultData.error));
      }
    } else {
      console.log('no execution_data for 616');
    }
    db.close();
  });
});
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');
const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READONLY, function(err) {
  db.get("SELECT data, workflowData FROM execution_data WHERE executionId=619", function(err, row) {
    if (err) { console.error(err.message); db.close(); return; }
    if (!row) { console.log('no row'); db.close(); return; }
    
    // Parse data column
    if (row.data) {
      try {
        var d = JSON.parse(row.data);
        console.log('data type:', typeof d);
        console.log('data keys:', Object.keys(d || {}));
        if (d.resultData) {
          console.log('lastNode:', d.resultData.lastNodeExecuted);
          if (d.resultData.error) {
            console.log('error.message:', d.resultData.error.message);
            console.log('error.lineNumber:', d.resultData.error.lineNumber);
          }
          // Get Extraer texto data
          var nodeData = d.resultData.runData && d.resultData.runData['Extraer texto'];
          if (nodeData) {
            console.log('Extraer texto data:', JSON.stringify(nodeData).substring(0, 500));
          }
        }
      } catch(e) {
        console.log('parse err:', e.message);
        console.log('raw data:', String(row.data).substring(0, 200));
      }
    } else {
      console.log('data is null');
    }
    db.close();
  });
});
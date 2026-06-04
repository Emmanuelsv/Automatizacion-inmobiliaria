const http = require('http');
const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/.pnpm/sqlite3@5.1.7/node_modules/sqlite3');

// Robust code that handles both formats and cannot throw on undefined
const ROBUST_CODE = [
  "const body = ($json && $json.body) ? $json.body : ($json || {});",
  "const messages = body.messages;",
  "if (!messages || !messages.length) {",
  "  return [{ json: { text: '', sender: '', groupId: '', pushName: '' } }];",
  "}",
  "const msg = messages[0];",
  "const text = (msg.text && msg.text.body) || msg.caption || '';",
  "const sender = msg.from || '';",
  "const groupId = msg.chat_id || body.id || '';",
  "const pushName = msg.from_name || '';",
  "return [{ json: { text, sender, groupId, pushName } }];"
].join('\n');

function login() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ emailOrLdapLoginId: 'admin@jhaen.com', password: 'Mye-n8n-2025!' });
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/login', method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } }, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve({ headers: res.headers, body: d }));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function patchViaAPI(cookie) {
  const wfRes = await new Promise((resolve, reject) => {
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'GET', headers: { Cookie: cookie } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.end();
  });
  const wf = JSON.parse(wfRes).data;
  const extraerIdx = wf.nodes.findIndex(n => n.name === 'Extraer texto');
  wf.nodes[extraerIdx].parameters.jsCode = ROBUST_CODE;

  const patchData = JSON.stringify({ nodes: wf.nodes, connections: wf.connections, settings: wf.settings, name: wf.name });
  const patchRes = await new Promise((resolve, reject) => {
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'PATCH', headers: { Cookie: cookie, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(patchData) } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject);
    req.write(patchData);
    req.end();
  });
  return JSON.parse(patchRes.body).data.versionId;
}

function syncAndCheckpoint(versionId) {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database('/home/node/.n8n/database.sqlite', sqlite3.OPEN_READWRITE, function(err) {
      if (err) { reject(err); return; }
      db.get("SELECT nodes FROM workflow_entity WHERE id='wS1VtPLDqJsZwu8y'", function(err, row) {
        if (err) { reject(err); db.close(); return; }
        var nodesStr = row.nodes;
        db.run("UPDATE workflow_history SET nodes=? WHERE versionId=?", [nodesStr, versionId], function(err2) {
          if (err2) { reject(err2); db.close(); return; }
          console.log('History updated rows:', this.changes);
          db.run("PRAGMA wal_checkpoint(FULL)", function(err3) {
            if (err3) { reject(err3); db.close(); return; }
            console.log('WAL checkpointed');
            db.close(function() { resolve(); });
          });
        });
      });
    });
  });
}

async function main() {
  console.log('Logging in...');
  const loginResult = await login();
  const cookie = loginResult.headers['set-cookie'][0].split(';')[0];

  console.log('Patching workflow via API...');
  const newVersionId = await patchViaAPI(cookie);
  console.log('New versionId:', newVersionId);

  console.log('Syncing workflow_history and checkpointing WAL...');
  await syncAndCheckpoint(newVersionId);

  console.log('Done. Ready to restart n8n.');
}

main().catch(console.error);
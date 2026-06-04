const http = require('http');

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

async function main() {
  const loginResult = await login();
  const cookie = loginResult.headers['set-cookie'][0].split(';')[0];

  const wfRes = await new Promise((resolve, reject) => {
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'GET', headers: { Cookie: cookie } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.end();
  });
  const wf = JSON.parse(wfRes).data;

  // Robust code that handles both $json.body.messages[] AND $json.messages[] AND chats_updates[]
  const robustCode = [
    "const root = $json.body || $json;",
    "const msgs = root.messages || (root.chats_updates && root.chats_updates[0] && [root.chats_updates[0].last_message]);",
    "if (!msgs || !msgs.length) return [{ json: { text: '', sender: '', groupId: '', pushName: '' } }];",
    "const msg = msgs[0];",
    "const text = (msg.text && msg.text.body) || msg.caption || '';",
    "const sender = msg.from || '';",
    "const groupId = $json.body ? $json.body.messages ? $json.body.messages[0].chat_id : root.id || '' : root.chat_id || '';",
    "const pushName = msg.from_name || '';",
    "return [{ json: { text, sender, groupId, pushName } }];"
  ].join('\n');

  const extraerIdx = wf.nodes.findIndex(n => n.name === 'Extraer texto');
  wf.nodes[extraerIdx].parameters.jsCode = robustCode;

  const patchData = JSON.stringify({ nodes: wf.nodes, connections: wf.connections, settings: wf.settings, name: wf.name });
  const patchRes = await new Promise((resolve, reject) => {
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'PATCH', headers: { Cookie: cookie, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(patchData) } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject);
    req.write(patchData);
    req.end();
  });
  console.log('Patch status:', patchRes.status);
  if (patchRes.status === 200) {
    const updated = JSON.parse(patchRes.body).data;
    const extraer = updated.nodes.find(n => n.name === 'Extraer texto');
    console.log('New versionId:', updated.versionId);
    console.log('New code first line:', extraer.parameters.jsCode.split('\n')[0]);
  }
}

main().catch(console.error);
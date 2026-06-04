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

function getWorkflow(cookie) {
  return new Promise((resolve, reject) => {
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'GET', headers: { Cookie: cookie } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.end();
  });
}

function patchWorkflow(cookie, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'PATCH', headers: { Cookie: cookie, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function main() {
  const loginResult = await login();
  const cookie = loginResult.headers['set-cookie'][0].split(';')[0];
  
  const wfBody = await getWorkflow(cookie);
  const wf = JSON.parse(wfBody).data;
  
  const extraerIdx = wf.nodes.findIndex(n => n.name === 'Extraer texto');
  
  // Debug code to understand what $json contains
  const debugCode = "console.log('$json keys:', Object.keys($json || {}));\nconsole.log('$json.body:', JSON.stringify($json.body || 'UNDEFINED'));\nconst msg = ($json.body || {}).messages ? $json.body.messages[0] : null;\nconsole.log('msg:', JSON.stringify(msg));\nreturn [{ json: { text: '', sender: '', groupId: '', pushName: '' } }];";
  
  wf.nodes[extraerIdx].parameters.jsCode = debugCode;
  
  // Try PATCH
  const patchResult = await patchWorkflow(cookie, { nodes: wf.nodes, connections: wf.connections, settings: wf.settings, name: wf.name });
  console.log('PATCH status:', patchResult.status);
  console.log('PATCH body (first 200):', patchResult.body.substring(0, 200));
}

main().catch(console.error);
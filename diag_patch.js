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
  
  // Get current workflow
  const wfRes = await new Promise((resolve, reject) => {
    const req = require('http').request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'GET', headers: { Cookie: cookie } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.end();
  });
  const wf = JSON.parse(wfRes).data;
  
  // Diagnostic code that throws a DESCRIPTIVE error to see $json structure
  const diagCode = 'const info = { type: typeof $json, keys: Object.keys($json || {}), bodyExists: !!($json && $json.body), bodyKeys: Object.keys(($json && $json.body) ? $json.body : {}), messagesExists: !!(($json && $json.body && $json.body.messages)), inputLen: $input && $input.all ? $input.all().length : -1 }; throw new Error("DIAG: " + JSON.stringify(info));';
  
  const extraerIdx = wf.nodes.findIndex(n => n.name === 'Extraer texto');
  wf.nodes[extraerIdx].parameters.jsCode = diagCode;
  
  const patchData = JSON.stringify({ nodes: wf.nodes, connections: wf.connections, settings: wf.settings, name: wf.name });
  const patchRes = await new Promise((resolve, reject) => {
    const req = require('http').request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'PATCH', headers: { Cookie: cookie, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(patchData) } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject);
    req.write(patchData);
    req.end();
  });
  console.log('Patch status:', patchRes.status);
}

main().catch(console.error);
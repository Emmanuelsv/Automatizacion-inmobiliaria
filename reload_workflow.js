const http = require('http');

function req(method, path, cookie, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const headers = { Cookie: cookie };
    if (data) { headers['Content-Type'] = 'application/json'; headers['Content-Length'] = Buffer.byteLength(data); }
    const r = http.request({ hostname: 'localhost', port: 5678, path, method, headers }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

async function main() {
  // Login
  const loginData = JSON.stringify({ emailOrLdapLoginId: 'admin@jhaen.com', password: 'Mye-n8n-2025!' });
  const loginRes = await new Promise((resolve, reject) => {
    const r = http.request({ hostname: 'localhost', port: 5678, path: '/rest/login', method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(loginData) } }, (res) => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ headers: res.headers, body: d }));
    });
    r.on('error', reject);
    r.write(loginData);
    r.end();
  });
  const cookie = loginRes.headers['set-cookie'][0].split(';')[0];
  
  // Get current workflow
  const wfRes = await req('GET', '/rest/workflows/wS1VtPLDqJsZwu8y', cookie);
  const wf = JSON.parse(wfRes.body).data;
  
  // Set correct code
  const correctCode = "const msg = $json.body.messages[0];\nconst text = msg.text?.body || msg.caption || '';\nconst sender = msg.from || '';\nconst groupId = msg.chat_id || '';\nconst pushName = msg.from_name || '';\n\nreturn [{ json: { text, sender, groupId, pushName } }];";
  const extraerIdx = wf.nodes.findIndex(n => n.name === 'Extraer texto');
  wf.nodes[extraerIdx].parameters.jsCode = correctCode;
  
  // 1. Deactivate
  console.log('Deactivating...');
  const deactRes = await req('PATCH', '/rest/workflows/wS1VtPLDqJsZwu8y/activate', cookie, { active: false });
  console.log('Deactivate status:', deactRes.status, deactRes.body.substring(0, 100));
  
  // 2. PATCH with correct code  
  console.log('Patching code...');
  const patchRes = await req('PATCH', '/rest/workflows/wS1VtPLDqJsZwu8y', cookie, { nodes: wf.nodes, connections: wf.connections, settings: wf.settings, name: wf.name });
  console.log('Patch status:', patchRes.status);
  
  // 3. Reactivate
  console.log('Reactivating...');
  const actRes = await req('PATCH', '/rest/workflows/wS1VtPLDqJsZwu8y/activate', cookie, { active: true });
  console.log('Reactivate status:', actRes.status, actRes.body.substring(0, 100));
  
  // 4. Verify
  const verifyRes = await req('GET', '/rest/workflows/wS1VtPLDqJsZwu8y', cookie);
  const updatedWf = JSON.parse(verifyRes.body).data;
  const updatedExtraer = updatedWf.nodes.find(n => n.name === 'Extraer texto');
  console.log('Verified code (first 60):', updatedExtraer.parameters.jsCode.substring(0, 60));
  console.log('Active:', updatedWf.active);
}

main().catch(console.error);
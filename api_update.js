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

function putWorkflow(cookie, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = http.request({ hostname: 'localhost', port: 5678, path: '/rest/workflows/wS1VtPLDqJsZwu8y', method: 'PUT', headers: { Cookie: cookie, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } }, (res) => {
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
  console.log('Found Extraer texto at index', extraerIdx);
  console.log('Current code (first 80):', wf.nodes[extraerIdx].parameters.jsCode.substring(0, 80));
  
  // Update with correct code
  const newCode = "const msg = $json.body.messages[0];\nconst text = msg.text?.body || msg.caption || '';\nconst sender = msg.from || '';\nconst groupId = msg.chat_id || '';\nconst pushName = msg.from_name || '';\n\nreturn [{ json: { text, sender, groupId, pushName } }];";
  wf.nodes[extraerIdx].parameters.jsCode = newCode;
  
  // PUT the updated workflow
  const putResult = await putWorkflow(cookie, wf);
  console.log('PUT status:', putResult.status);
  if (putResult.status !== 200) {
    console.log('PUT error:', putResult.body.substring(0, 300));
  } else {
    const updated = JSON.parse(putResult.body).data;
    const updatedExtraer = updated.nodes.find(n => n.name === 'Extraer texto');
    console.log('Updated code (first 80):', updatedExtraer.parameters.jsCode.substring(0, 80));
  }
}

main().catch(console.error);
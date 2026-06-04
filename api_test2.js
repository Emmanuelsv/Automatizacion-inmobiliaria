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
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  const loginResult = await login();
  const cookie = loginResult.headers['set-cookie'][0].split(';')[0];
  const wfBody = await getWorkflow(cookie);
  const wf = JSON.parse(wfBody);
  console.log('wf keys:', Object.keys(wf).join(', '));
  if (wf.data) console.log('data keys:', Object.keys(wf.data).join(', '));
}

main().catch(console.error);
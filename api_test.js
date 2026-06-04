const http = require('http');

function post(path, body, headers) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const opts = {
      hostname: 'localhost', port: 5678, path, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data), ...headers }
    };
    const req = http.request(opts, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: d }));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function get(path, headers) {
  return new Promise((resolve, reject) => {
    const opts = { hostname: 'localhost', port: 5678, path, method: 'GET', headers: { 'Content-Type': 'application/json', ...headers } };
    const req = http.request(opts, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: d }));
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  // Login
  const loginResp = await post('/rest/login', { emailOrLdapLoginId: 'admin@jhaen.com', password: 'Mye-n8n-2025!' });
  console.log('login status:', loginResp.status);
  
  // Extract auth token from cookie
  const setCookie = loginResp.headers['set-cookie'] || [];
  console.log('cookies:', JSON.stringify(setCookie));
  
  // Try n8n-auth cookie or browse_n8n_id
  const cookieHeader = setCookie.map(c => c.split(';')[0]).join('; ');
  console.log('using cookie:', cookieHeader);
  
  // Get workflow
  const wfResp = await get('/rest/workflows/wS1VtPLDqJsZwu8y', { Cookie: cookieHeader });
  console.log('workflow status:', wfResp.status);
  if (wfResp.status === 200) {
    const wf = JSON.parse(wfResp.body);
    const extraer = wf.nodes.find(n => n.name === 'Extraer texto');
    console.log('current code:', extraer.parameters.jsCode.substring(0, 80));
  } else {
    console.log('error:', wfResp.body.substring(0, 200));
  }
}

main().catch(console.error);
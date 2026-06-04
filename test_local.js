const http = require('http');
const payload = JSON.stringify({ messages: [{ chat_id: "120363@g.us", from: "573026218105", from_name: "Test", text: { body: "apartamento laureles 2 hab 400 millones" } }] });
const req = http.request({ hostname: 'localhost', port: 5678, path: '/webhook/whatsapp-inmobiliaria', method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) } }, (res) => {
  let d = ''; res.on('data', c => d += c); res.on('end', () => console.log('STATUS:', res.statusCode, 'BODY:', d));
});
req.on('error', e => console.error('ERROR:', e.message));
req.write(payload);
req.end();
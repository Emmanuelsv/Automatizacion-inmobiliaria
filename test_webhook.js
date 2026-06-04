const http = require('http');

const payload = JSON.stringify({
  messages: [{
    chat_id: "120363123456789012@g.us",
    from: "573026218105",
    from_name: "Test Asesor",
    text: { body: "Buenas, busco apartamento en Laureles 2 habitaciones hasta 500 millones, cliente: Juan Perez, tel: 3001234567" }
  }]
});

const options = {
  hostname: 'localhost',
  port: 5678,
  path: '/webhook/whatsapp-inmobiliaria',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload)
  }
};

const req = http.request(options, (res) => {
  let d = '';
  res.on('data', c => d += c);
  res.on('end', () => console.log('STATUS:', res.statusCode, 'BODY:', d));
});
req.on('error', e => console.error('ERROR:', e.message));
req.write(payload);
req.end();
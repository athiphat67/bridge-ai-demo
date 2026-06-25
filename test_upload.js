const axios = require('axios');
const FormData = require('form-data');

async function run() {
  const form = new FormData();
  form.append('mode', 'real');
  
  // Create a 5MB buffer to test size limits
  const buffer = Buffer.alloc(5 * 1024 * 1024, 'a');
  form.append('image', buffer, 'large.png');
  
  form.append('age_years', '8');
  form.append('gender', 'male');
  form.append('weight_kg', '30');
  form.append('height_cm', '128');
  form.append('location', 'medial');

  try {
    const res = await axios.post('http://localhost:5173/api/analyze', form, {
      headers: form.getHeaders(),
    });
    console.log('STATUS:', res.status);
    console.log('DATA:', res.data);
  } catch (err) {
    console.log('ERROR:', err.response ? err.response.status : err.message);
    if (err.response) console.log('DETAIL:', err.response.data);
  }
}
run();

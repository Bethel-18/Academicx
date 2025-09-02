/* main.js - front-end JS for academix (calls Django API) */
const setToken = t => t ? localStorage.setItem('academix_token', t) : localStorage.removeItem('academix_token');
const getToken = () => localStorage.getItem('academix_token');

async function postJSON(path, body){
  const headers = {'Content-Type':'application/json'};
  const token = getToken();
  if(token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(path, {method:'POST', headers, body: JSON.stringify(body)});
  return res.json();
}
async function getJSON(path){ 
  const headers = {};
  const token = getToken();
  if(token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(path, {headers});
  return res.json();
}
function renderCards(cards){
  const container = document.getElementById('cards');
  container.innerHTML = '';
  (cards || []).forEach(c=>{
    const col = document.createElement('div');
    col.className = 'col-12 mb-2';
    col.innerHTML = `<div class="card"><div class="card-body"><strong>Q:</strong><div>${c.question}</div><hr/><strong>A:</strong><div>${c.answer}</div></div></div>`;
    container.appendChild(col);
  });
}

document.getElementById('genBtn').addEventListener('click', async ()=>{
  const notes = document.getElementById('notes').value;
  const data = await postJSON('/api/generate/', {notes});
  renderCards(data.flashcards || []);
});

document.getElementById('saveBtn').addEventListener('click', async ()=>{
  const cards = Array.from(document.querySelectorAll('#cards .card')).map(card=>{
    const q = card.querySelector('div div')?.innerText || '';
    const a = card.querySelector('div div + hr + div')?.innerText || '';
    // fallback: parse by positions (works with current structure)
    const qs = card.querySelectorAll('.card-body > div');
    return {question: qs[0]?.innerText || '', answer: qs[1]?.innerText || ''};
  });
  const res = await postJSON('/api/flashcards/', {flashcards: cards});
  if(res.error) alert('Save failed: ' + res.error);
  else alert('Saved ' + (res.saved ? res.saved.length : 0) + ' cards');
});

document.getElementById('editable').addEventListener('mouseup', async ()=>{
  const sel = window.getSelection().toString().trim();
  if(!sel) return;
  const data = await postJSON('/api/generate/', {notes: sel});
  const first = (data.flashcards && data.flashcards[0]) || null;
  document.getElementById('explain').innerText = first ? first.answer : 'No explanation';
});

// Auth handlers
document.getElementById('regBtn').addEventListener('click', async ()=>{
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const email = document.getElementById('email').value;
  const res = await postJSON('/api/register/', {username, password, email});
  if(res.error) return alert(res.error);
  alert('Registered — now login to get a token');
});
document.getElementById('loginBtn').addEventListener('click', async ()=>{
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await postJSON('/api/token/', {username, password});
  if(res.detail || !res.access) return alert('Login failed');
  setToken(res.access);
  document.getElementById('userInfo').innerText = 'Logged in';
  alert('Logged in');
});
document.getElementById('logoutBtn').addEventListener('click', ()=>{
  setToken(null);
  document.getElementById('userInfo').innerText = '';
  alert('Logged out');
});

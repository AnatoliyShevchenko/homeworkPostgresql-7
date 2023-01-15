const token = document.getElementById('token');
const user_id = document.getElementById('user_id');
localStorage.setItem('user_id', user_id.value);
localStorage.setItem('token', token.value);
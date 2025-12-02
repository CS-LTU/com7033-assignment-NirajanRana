// main.js - handles expenses table loading and basic actions
async function loadExpenses(mine=true){
  const url = mine ? '/api/expenses?mine=1' : '/api/expenses';
  const res = await fetch(url);
  const data = await res.json();
  const tbody = document.querySelector('#tbl tbody');
  tbody.innerHTML = '';
  data.forEach(d => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${d._id}</td>
      <td>${d.name}</td>
      <td>${d.product || ''}</td>
      <td>${d.expense || 0}</td>
      <td>
        <button class="btn btn-sm btn-warning" onclick="editExpense('${d._id}')">Edit</button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteExpense('${d._id}')">Delete</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

async function editExpense(id){
  // Redirect user to the update page
  window.location.href = "/update_expense/" + id;
}

async function deleteExpense(id){
  if(!confirm('Delete this expense?')) return;
  const res = await fetch('/api/expense/' + id, { method: 'DELETE' });
  if(res.ok) loadExpenses(true);
}

document.addEventListener('DOMContentLoaded', function(){
  const loadMine = document.getElementById('loadMine');
  const loadAll = document.getElementById('loadAll');
  if(loadMine) loadMine.addEventListener('click', () => loadExpenses(true));
  if(loadAll) loadAll.addEventListener('click', () => loadExpenses(false));

  // auto load mine on expenses page
  if(document.querySelector('#tbl')) loadExpenses(true);
});

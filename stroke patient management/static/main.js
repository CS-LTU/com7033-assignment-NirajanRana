async function loadPatientData(mine = true) {
    const url = mine ? '/api/patient_data?mine=1' : '/api/patient_data';
    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.querySelector('#tbl tbody');
    tbody.innerHTML = '';

    data.forEach(d => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${d.id}</td>
            <td>${d.gender}</td>
            <td>${d.age}</td>
            <td>${d.hypertension}</td>
            <td>${d.heart_disease}</td>
            <td>${d.ever_married}</td>
            <td>${d.work_type}</td>
            <td>${d.Residence_type}</td>
            <td>${d.avg_glucose_level}</td>
            <td>${d.bmi}</td>
            <td>${d.smoking_status}</td>
            <td>${d.stroke}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editPatient('${d._id}')">Edit</button>
                <button class="btn btn-sm btn-outline-danger" onclick="deletePatient('${d._id}')">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function editPatient(id) {
    window.location.href = "/update_patient_data/" + id;
}

async function deletePatient(id) {
    if (!confirm('Delete this patient record?')) return;

    const res = await fetch('/api/patient_data/' + id, { method: 'DELETE' });
    if (res.ok) {
        alert("Record deleted successfully");
        loadPatientData(true);
    } else {
        const err = await res.json();
        alert("Error: " + (err.error || "Could not delete record"));
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function () {
    const loadMine = document.getElementById('loadMine');
    const loadAll = document.getElementById('loadAll');

    if (loadMine) loadMine.addEventListener('click', () => loadPatientData(true));
    if (loadAll) loadAll.addEventListener('click', () => loadPatientData(false));

    // Load My Records by default
    if (document.querySelector('#tbl')) loadPatientData(true);
});

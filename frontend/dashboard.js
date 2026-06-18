const API_URL = "";

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}

// =========================
// LOAD USERNAME
// =========================

document.getElementById("username").innerText =
    localStorage.getItem("username");

// =========================
// DASHBOARD STATS
// =========================

async function loadStats() {

    try {

        const response = await fetch(
            `${API_URL}/dashboard/stats`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        document.getElementById(
            "studentsCount"
        ).innerText = data.students || 0;

        document.getElementById(
            "attendanceCount"
        ).innerText = data.attendance || 0;

        document.getElementById(
            "marksCount"
        ).innerText = data.marks || 0;

    } catch (error) {

        console.log(error);

    }
}

// =========================
// LOAD STUDENTS
// =========================

let allStudents = [];

async function loadStudents() {
    try {
        const response = await fetch(`${API_URL}/students`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        allStudents = await response.json();
        renderStudents(allStudents);
    } catch (error) {
        console.log(error);
    }
}

function renderStudents(students) {
    if (!Array.isArray(students)) {
        console.error("Expected array but got:", students);
        return;
    }
    let rows = "";
    students.forEach((student, index) => {
        rows += `
        <tr>
            <td>${index + 1}</td>
            <td>${student.student_id}</td>
            <td>${student.full_name}</td>
            <td>${student.email}</td>
            <td>${student.course}</td>
            <td>
                <button class="action-btn edit" onclick="openEditModal(${student.id})">Edit</button>
                <button class="action-btn delete" onclick="deleteStudent(${student.id})">Delete</button>
            </td>
        </tr>
        `;
    });
    document.getElementById("studentTable").innerHTML = rows;
}

// =========================
// SEARCH STUDENT
// =========================

async function searchStudent() {
    const keyword = document.getElementById("searchInput").value;

    if (keyword.trim() === "") {
        loadStudents();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/search/${keyword}`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const students = await response.json();
        renderStudents(students);
    } catch (error) {
        console.log(error);
    }
}

// =========================
// DELETE STUDENT
// =========================

async function deleteStudent(id) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete?"
        );

    if (!confirmDelete) return;

    try {

        const response =
            await fetch(
                `${API_URL}/students/${id}`, {
                    method: "DELETE",

                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

        const data =
            await response.json();

        alert(data.message);

        loadStudents();
        loadStats();

    } catch (error) {

        console.log(error);

    }
}

// =========================
// MODAL LOGIC
// =========================

function openAddModal() {
    document.getElementById("modalTitle").innerText = "Add New Student";
    document.getElementById("studentForm").reset();
    document.getElementById("editId").value = "";
    document.getElementById("studentModal").style.display = "block";
}

function openEditModal(id) {
    const student = allStudents.find(s => s.id === id);
    if (!student) return;

    document.getElementById("modalTitle").innerText = "Edit Student";
    document.getElementById("editId").value = student.id;
    document.getElementById("student_id_input").value = student.student_id;
    document.getElementById("full_name").value = student.full_name;
    document.getElementById("email").value = student.email;
    document.getElementById("course").value = student.course;
    document.getElementById("phone").value = student.phone || "";
    document.getElementById("address").value = student.address || "";

    document.getElementById("studentModal").style.display = "block";
}

function closeModal() {
    document.getElementById("studentModal").style.display = "none";
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById("studentModal");
    if (event.target == modal) {
        closeModal();
    }
}

// =========================
// FORM SUBMISSION
// =========================

document.getElementById("studentForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const id = document.getElementById("editId").value;
    const studentData = {
        student_id: document.getElementById("student_id_input").value,
        full_name: document.getElementById("full_name").value,
        email: document.getElementById("email").value,
        course: document.getElementById("course").value,
        phone: document.getElementById("phone").value,
        address: document.getElementById("address").value
    };

    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/students/${id}` : `${API_URL}/students`;

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(studentData)
        });

        const data = await response.json();
        if (data.success) {
            alert(data.message);
            closeModal();
            loadStudents();
            loadStats();
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.log(error);
        alert("Server Error");
    }
});

// =========================
// LOGOUT
// =========================

function logout() {

    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");

    window.location.href =
        "login.html";
}

// =========================
// INITIAL LOAD
// =========================

loadStats();
loadStudents();
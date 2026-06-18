const API_URL = "";

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}

// =========================
// LOAD STUDENTS FOR DROPDOWN
// =========================
async function loadStudentsList() {
    try {
        const response = await fetch(`${API_URL}/students`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }

        const students = await response.json();
        let options = '<option value="">-- Choose Student --</option>';
        
        students.forEach(student => {
            options += `<option value="${student.id}">${student.student_id} - ${student.full_name}</option>`;
        });

        document.getElementById("student_id").innerHTML = options;
    } catch (error) {
        console.error("Error loading students:", error);
    }
}

// =========================
// LOAD ATTENDANCE RECORDS
// =========================
async function loadAttendance() {
    try {
        const response = await fetch(`${API_URL}/attendance`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }

        const records = await response.json();
        
        if (!Array.isArray(records)) {
            console.error("Failed to load records", records);
            document.getElementById("attendanceTable").innerHTML = `<tr><td colspan="5">No records found</td></tr>`;
            return;
        }

        let rows = "";
        records.forEach((record, index) => {
            rows += `
            <tr>
                <td>${index + 1}</td>
                <td style="font-weight: 600; color: #2563eb;">${record.roll_no}</td>
                <td>${record.full_name}</td>
                <td>${record.attendance_date}</td>
                <td>
                    <span class="status-badge ${record.status.toLowerCase()}" 
                          style="padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; 
                          background: ${record.status === 'Present' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'}; 
                          color: ${record.status === 'Present' ? '#10b981' : '#ef4444'};">
                        ${record.status}
                    </span>
                </td>
            </tr>
            `;
        });

        document.getElementById("attendanceTable").innerHTML = rows || '<tr><td colspan="5">No attendance records found.</td></tr>';
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Could not load attendance data.");
    }
}

// =========================
// SAVE ATTENDANCE
// =========================
document.getElementById("attendanceForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const attendanceData = {
        student_id: document.getElementById("student_id").value,
        attendance_date: document.getElementById("attendance_date").value,
        status: document.getElementById("status").value
    };

    try {
        const response = await fetch(`${API_URL}/attendance`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(attendanceData)
        });

        const data = await response.json();
        
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }

        if (data.success) {
            alert("Attendance marked successfully!");
            document.getElementById("attendanceForm").reset();
            // Set today's date automatically after reset if preferred
            loadAttendance();
        } else {
            alert("Error: " + (data.message || "Failed to save attendance"));
        }
    } catch (error) {
        console.error("Save Error:", error);
        alert("Server connection failed. Please ensure the backend is running.");
    }
});

// Set default date to today
document.getElementById("attendance_date").valueAsDate = new Date();

// Initialize
loadStudentsList();
loadAttendance();

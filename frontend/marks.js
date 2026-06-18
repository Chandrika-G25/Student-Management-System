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
// LOAD MARKS RECORDS
// =========================
async function loadMarks() {
    try {
        const response = await fetch(`${API_URL}/marks`, {
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
            document.getElementById("marksTable").innerHTML = `<tr><td colspan="6">No records found</td></tr>`;
            return;
        }

        let rows = "";
        records.forEach(record => {
            const percentage = ((record.marks_obtained / record.total_marks) * 100).toFixed(1);
            let statusColor = "#10b981"; // Success
            if (percentage < 40) statusColor = "#ef4444"; // Danger
            else if (percentage < 70) statusColor = "#f59e0b"; // Warning

            rows += `
            <tr>
                <td style="font-weight: 600; color: #2563eb;">${record.roll_no}</td>
                <td>${record.full_name}</td>
                <td>${record.exam_name}</td>
                <td>${record.subject}</td>
                <td>${record.marks_obtained} / ${record.total_marks}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="flex: 1; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden;">
                            <div style="width: ${percentage}%; height: 100%; background: ${statusColor};"></div>
                        </div>
                        <span style="font-weight: 700; color: ${statusColor}; min-width: 45px;">${percentage}%</span>
                    </div>
                </td>
            </tr>
            `;
        });

        document.getElementById("marksTable").innerHTML = rows || '<tr><td colspan="6">No marks recorded found.</td></tr>';
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Could not load marks data.");
    }
}

// =========================
// SAVE MARKS
// =========================
document.getElementById("marksForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const marksData = {
        student_id: document.getElementById("student_id").value,
        exam_name: document.getElementById("exam_name").value,
        subject: document.getElementById("subject").value,
        marks_obtained: document.getElementById("marks_obtained").value,
        total_marks: document.getElementById("total_marks").value
    };

    try {
        const response = await fetch(`${API_URL}/marks`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(marksData)
        });

        const data = await response.json();
        
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }

        if (data.success) {
            alert("Marks saved successfully!");
            document.getElementById("marksForm").reset();
            document.getElementById("total_marks").value = 100;
            loadMarks();
        } else {
            alert("Error: " + (data.message || "Failed to save marks"));
        }
    } catch (error) {
        console.error("Save Error:", error);
        alert("Server connection failed.");
    }
});

// Initialize
loadStudentsList();
loadMarks();

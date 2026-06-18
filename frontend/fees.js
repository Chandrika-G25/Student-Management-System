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
// LOAD FEES RECORDS
// =========================
async function loadFees() {
    try {
        const response = await fetch(`${API_URL}/fees`, {
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
            document.getElementById("feesTable").innerHTML = `<tr><td colspan="7">No records found</td></tr>`;
            return;
        }

        let rows = "";
        records.forEach(record => {
            const balance = record.total_fee - record.paid_amount;
            const status = balance <= 0 ? "Fully Paid" : "Partial";
            const statusColor = balance <= 0 ? "#10b981" : "#f59e0b";

            rows += `
            <tr>
                <td style="font-weight: 600; color: #2563eb;">${record.roll_no}</td>
                <td>${record.full_name}</td>
                <td>₹${parseFloat(record.total_fee).toLocaleString()}</td>
                <td style="color: #10b981; font-weight: 600;">₹${parseFloat(record.paid_amount).toLocaleString()}</td>
                <td style="color: ${balance > 0 ? '#ef4444' : '#10b981'}; font-weight: 600;">₹${parseFloat(balance).toLocaleString()}</td>
                <td>
                    <span style="padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; background: ${balance <= 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)'}; color: ${statusColor};">
                        ${status}
                    </span>
                </td>
                <td>${record.payment_date}</td>
            </tr>
            `;
        });

        document.getElementById("feesTable").innerHTML = rows || '<tr><td colspan="7">No payment history found.</td></tr>';
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Could not load fee data.");
    }
}

// =========================
// SAVE PAYMENT
// =========================
document.getElementById("feeForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const feeData = {
        student_id: document.getElementById("student_id").value,
        total_fee: document.getElementById("total_fee").value,
        paid_amount: document.getElementById("paid_amount").value,
        payment_method: document.getElementById("payment_method").value,
        payment_date: document.getElementById("payment_date").value
    };

    try {
        const response = await fetch(`${API_URL}/fees`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(feeData)
        });

        const data = await response.json();
        
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }

        if (data.success) {
            alert("Payment recorded successfully!");
            document.getElementById("feeForm").reset();
            document.getElementById("payment_date").valueAsDate = new Date();
            loadFees();
        } else {
            alert("Error: " + (data.message || "Failed to save payment"));
        }
    } catch (error) {
        console.error("Save Error:", error);
        alert("Server connection failed.");
    }
});

// Set default date to today
document.getElementById("payment_date").valueAsDate = new Date();

// Initialize
loadStudentsList();
loadFees();

document.addEventListener("DOMContentLoaded", () => {
    console.log("Script Loaded!");

    // If on the Dashboard page, fetch notifications every 5 seconds
    if (document.getElementById("notifications")) {
        setInterval(fetchNotifications, 5000);
    }

    // If on the Register page, handle form submission
    if (document.getElementById("register-form")) {
        document.getElementById("register-form").addEventListener("submit", registerEmployee);
    }

    // If on the Attendance Log page, fetch attendance data
    if (document.getElementById("attendance-body")) {
        fetchAttendanceData();
    }
});

// Fetch and display notifications
function fetchNotifications() {
    fetch("/notifications")
        .then(response => response.json())
        .then(data => {
            console.log("Notifications received:", data);
            const notifList = document.getElementById("notifications");
            notifList.innerHTML = "";
            data.forEach(msg => {
                let li = document.createElement("li");
                li.className = "list-group-item";
                li.innerText = msg;
                notifList.appendChild(li);
            });
        })
        .catch(err => console.error("Error fetching notifications:", err));
}

// Handle Employee Registration Form Submission
function registerEmployee(event) {
    event.preventDefault();
    let formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("photo", document.getElementById("photo").files[0]);

    fetch("/register", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Registration Response:", data);
        let flash = document.getElementById("flash-message");
        flash.innerHTML = `<div class="alert alert-${data.status}">${data.message}</div>`;
        setTimeout(() => flash.innerHTML = "", 3000);
    })
    .catch(err => console.error("Error registering employee:", err));
}

// Fetch and display attendance data
function fetchAttendanceData() {
    fetch("/attendance_data")
        .then(response => response.json())
        .then(data => {
            console.log("Attendance Data:", data);
            const tbody = document.getElementById("attendance-body");
            tbody.innerHTML = "";
            data.forEach(entry => {
                let row = `<tr>
                    <td>${entry.name}</td>
                    <td>${entry.check_in}</td>
                    <td>${entry.check_out || 'N/A'}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        })
        .catch(err => console.error("Error fetching attendance data:", err));
}

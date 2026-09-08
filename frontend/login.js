document
    .getElementById("loginForm")
    .addEventListener("submit", login);

async function login(e) {

    e.preventDefault();

    const email =
        document.getElementById("email").value;

    const password =
        document.getElementById("password").value;

    try {

        const response =
            await fetch(
                "/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email,
                        password
                    })
                });

        const data =
            await response.json();

        if (data.success) {

            localStorage.setItem(
                "token",
                data.token
            );

            localStorage.setItem(
                "role",
                data.role
            );

            localStorage.setItem(
                "username",
                data.username
            );

            window.location.href =
                "dashboard.html";

        } else {

            document.getElementById(
                    "errorMsg"
                ).innerText =
                data.message;
        }

    } catch (error) {

        document.getElementById(
                "errorMsg"
            ).innerText =
            "Server Error";
    }
}
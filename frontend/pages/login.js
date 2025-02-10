import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { io } from "socket.io-client"

export default function Login() {
    const [login, setLogin] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [socket, setSocket] = useState(null);
    const router = useRouter();

    useEffect(() => {
      const newSocket = io("ws://127.0.0.1:5000");
      setSocket(newSocket);

    }, [])

    const handleLogin = async () => {
        const res = await fetch("http://127.0.0.1:5000/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ login, password }),
        });
        const data = await res.json();
        if (data.success) {
            sessionStorage.setItem("role", data.role);
            sessionStorage.setItem("login", data.username);
            sessionStorage.setItem("password", data.password);

              if (socket) {
                socket.emit("login", sessionStorage.getItem("login"));
              }

            if (data.role === "administrator") {
              router.push("/adminDashboard")
            } else {
              router.push("/menu")
            }
            
        } else {
            setError(data.message)
        }
    }
    return (
        <div>
          <h2>Logowanie</h2>
          <input type="text" placeholder="Login" value={login} onChange={(e) => setLogin(e.target.value)} />
          <input type="password" placeholder="Hasło" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <p>{error}</p>}
          <button onClick={handleLogin}>Zaloguj</button>
          <button onClick={() => router.push("/")}>Wróć do strony głównej</button>
        </div>
      );
}
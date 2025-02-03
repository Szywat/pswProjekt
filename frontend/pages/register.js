import { useState } from "react";
import { useRouter } from "next/router";

export default function Register() {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleRegister = async () => {
    const res = await fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password }),
    });

    const data = await res.json();
    if (data.success) {
      router.push("/login");
    } else {
      setError(data.message);
    }
  };

  return (
    <div>
      <h2>Rejestracja</h2>
      <input type="text" placeholder="Login" value={login} onChange={(e) => setLogin(e.target.value)} />
      <input type="password" placeholder="Hasło" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <p>{error}</p>}
      <button onClick={handleRegister}>Zarejestruj</button>
      <button onClick={() => router.push("/")}>Wróć do strony głównej</button>
    </div>
  );
}

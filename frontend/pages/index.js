import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();

  return (
    <div>
      <h1>Restauracja</h1>
      <button onClick={() => router.push("/login")}>Zaloguj się</button>
      <button onClick={() => router.push("/register")}>Zarejestruj się</button>
    </div>
  );
}

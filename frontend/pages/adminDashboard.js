import { useEffect } from "react";
import { useRouter } from "next/router";
import Logout from "../components/LogOut"

export default function Dashboard() {
  const router = useRouter();

  useEffect(() => {
    const role = sessionStorage.getItem("role");
    if (role !== "administrator") {
      router.push("/menu");
    }
  }, [router]);

  return (
    <div>
      <h1>Panel Administratora</h1>

      <Logout router={router}/>
    </div>
  );
}

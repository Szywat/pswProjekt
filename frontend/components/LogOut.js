import { io } from "socket.io-client"
import { useEffect, useState } from "react";
export default function Logout({ router }) {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io("wss://127.0.0.1:5000");
    setSocket(newSocket);

  }, []);

  const handleLogout = () => {
    if (socket) {
      socket.emit("logout", sessionStorage.getItem("login"));
    }
    sessionStorage.removeItem("login")
    sessionStorage.removeItem("role")
    sessionStorage.removeItem("password")
    
    router.push("/");
  };

  return (
    <button onClick={handleLogout}>Wyloguj</button>
  )
}
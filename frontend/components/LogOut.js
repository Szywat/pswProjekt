import { io } from "socket.io-client"
import { useEffect, useState } from "react";
import Cookies from "js-cookie";
export default function Logout({ router }) {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io("ws://127.0.0.1:5000");
    setSocket(newSocket);

  }, []);

  const handleLogout = () => {
    if (socket) {
      socket.emit("logout", Cookies.get("login"));
    }
    Cookies.remove("login")
    Cookies.remove("role")
    Cookies.remove("password")
    
    router.push("/");
  };

  return (
    <button onClick={handleLogout}>Wyloguj</button>
  )
}
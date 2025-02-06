import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Cookies from "js-cookie";
import Logout from "../components/LogOut"

export default function Dashboard() {
  const router = useRouter();
  const [orderList, setOrderList] = useState([]);

  useEffect(() => {
    const role = Cookies.get("role");
    if (role !== "administrator") {
      router.push("/menu");
    }
  }, [router]);

  const getOrders = async () => {
    const res = await fetch("http://127.0.0.1:5000/order/orders", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    })
    const data = await res.json()
    setOrderList(data || []);
    
  }

  const removeOrder = async (index) => {
    const res = await fetch("http://127.0.0.1:5000/order/orders", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index }),
    })

    if (res.ok) {
      setOrderList((prevOrders) => prevOrders.filter((_, i) => i !== index));
    }
  }

  return (
    <div>
      <h1>Panel Administratora</h1>
      <button onClick={getOrders}>Załaduj zamówienia</button>
      <Logout router={router} />
      {orderList.map((order, index) => (
        <ul key={index}>
          <li><strong>{order.user}</strong></li>
          {Object.entries(order.items).map(([product, quantity]) => (
            <li key={product}>
              {product} x {quantity}
            </li>
          ))}
          <button onClick={() => removeOrder(index)}>Usuń zamówienie</button>
        </ul>
      ))}
    </div>
  );
}
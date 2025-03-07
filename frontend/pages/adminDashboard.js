import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/router";
import Logout from "../components/LogOut";
import Filter from "../components/Filter";
import Chat from "../components/Chat"

export default function Dashboard() {
  const router = useRouter();
  const [orderList, setOrderList] = useState([]);

  useEffect(() => {
    const role = sessionStorage.getItem("role");
    if (role !== "administrator") {
      router.push("/menu");
    }

  }, [router]);

  const getOrders = async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const res = await fetch(`http://127.0.0.1:5000/order/orders?${params}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    })
    const data = await res.json()
    setOrderList(data || []);
    console.log(data);
    
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
    <> 
    <div>
      <h1>Panel Administratora</h1>
      <Logout router={router} />
      <Filter updateFilters={getOrders} />
      <h2>Lista zamówień:</h2>
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
    < Chat />
    </>
   
  );
}
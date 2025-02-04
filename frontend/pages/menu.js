import { useState, useEffect } from "react"
import { useRouter } from "next/router";
import LogOut from "../components/LogOut"
export default function Menu() {
    const router = useRouter();
    const [products, setProducts] = useState([]);
    const [order, setOrder] = useState({});
    const [username, setUsername] = useState("");
    const [history, setHistory] = useState([]);

    useEffect(() => {
        if (typeof window !== "undefined") {
            const storedUsername = sessionStorage.getItem("username");
            
            if (storedUsername) {
                setUsername(storedUsername);
                fetchUserOrders(storedUsername);
            }
        }
    }, []);

    const fetchOrders = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5000/order/products", {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            })

            if (!res.ok) {
                throw new Error("Błąd podczas pobierania produktów");
              }

            const data = await res.json();
            setProducts(data.products || []);
        } catch (error) {
            console.error("Błąd: ", error);
        }
    };

    const addToOrder = (product) => {
        if (product.count === 0) return;
        setProducts(prevProducts => 
            prevProducts.map(p =>
                p.product === product.product && p.count > 0 ? { ...p, count: p.count -1} : p
            )
        );

        setOrder(prevOrder => ({
            ...prevOrder,
            [product.product]: (prevOrder[product.product] || 0) + 1
        }));
        updateProductCount(product.product, product.count - 1);
    };

    const placeOrder = async () => {
        try {
            const res = await fetch(`http://127.0.0.1:5000/order/user/${username}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "items": order }),
            });
    
            if (!res.ok) {
                throw new Error("Błąd podczas składania zamówienia");
            }
    
            setHistory(prevHistory => [...prevHistory, { items: order}]);
            setOrder({});
            fetchUserOrders(username); // Aktualizacja historii zamówień
        } catch (error) {
            console.error("Błąd składania zamówienia:", error);
        }
    };

    const fetchUserOrders = async (username) => {
        try {
            const res = await fetch(`http://127.0.0.1:5000/order/user/${username}`, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });
    
            if (!res.ok) {
                throw new Error("Błąd podczas pobierania zamówień");
            }
    
            const data = await res.json();
            setHistory(data.orders || []);
        } catch (error) {
            console.error("Błąd: ", error);
        }
    };

    const updateProductCount = async (productName, newCount) => {
        try {
            await fetch("http://127.0.0.1:5000/order/products", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ product: productName, count: newCount }),
            });
        } catch (error) {
            console.error("Błąd aktualizacji produktu:", error);
        }
    };

    return (
        <div>
            <h2>Menu</h2>
            <ul className="products">
                {products.map((product, index) => (
                    product.count > 0 && (
                        <li key={index} onClick={() => addToOrder(product)}>
                            {product.product} (Ilość: {product.count})
                        </li>
                    )
                ))}
            </ul>
            <button onClick={fetchOrders}>Złóż zamówienie</button>
            <LogOut router={router}/>

            <h3>Twoje zamówienie:</h3>
            <ul>
                {Object.entries(order).map(([product, quantity]) => (
                    <li key={product}>{product} x {quantity}</li>
                ))}
            </ul>

            {Object.keys(order).length > 0 && (
                <button onClick={placeOrder}>Zamawiam</button>
            )}
            <h3>Złożone zamówienia:</h3>
            <ul>
                {history.map((ord, index) => (
                    <li key={index}>
                        <strong>Zamówienie {index + 1}:</strong>
                        <ul>
                            {Object.entries(ord.items).map(([product, quantity]) => (
                                <li key={product}>{product} x {quantity}</li>
                            ))}
                        </ul>
                    </li>
                ))}
            </ul>
        </div>

    )
}
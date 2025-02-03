export default function Logout({ router }) {
    return (
        <button onClick={() => {
            sessionStorage.removeItem("role");
            router.push("/");
          }}>
            Wyloguj
          </button>
    )
}
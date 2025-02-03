export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <main className="bg-white p-6 rounded shadow-md">{children}</main>
    </div>
  );
}

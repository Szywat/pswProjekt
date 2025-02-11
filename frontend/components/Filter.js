"use client";

import { useState } from "react";

export default function Filter({ updateFilters }) {
  const [search, setSearch] = useState("");

  const applyFilters = () => {
    updateFilters({ search });
  };

  return (
    <div className="filter-bar">
      <h2>Szukaj zamówień</h2>
      <div className="filter-name">
        <label>Po użytkowniku: </label>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder=""
        />
      </div>
      <button onClick={applyFilters} className="filter-button">Szukaj</button>
    </div>
  );
}
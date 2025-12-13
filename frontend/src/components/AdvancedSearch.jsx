// src/components/AdvancedSearch.jsx
import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { axiosInstance } from "../utils/axiosHelper";

const AdvancedSearch = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState({
    searchText: "",
    category: "",
    priceTier: "",
    maxSweetness: 10,
    minCaffeine: 0,
    maxCaffeine: 400,
    isAlcoholic: false,
    excludedIngredients: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSearchParams((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const params = {
        search_text: searchParams.searchText || undefined,
        category: searchParams.category || undefined,
        price_tier: searchParams.priceTier || undefined,
        max_sweetness: searchParams.maxSweetness === 10 ? undefined : searchParams.maxSweetness,
        min_caffeine: searchParams.minCaffeine === 0 ? undefined : searchParams.minCaffeine,
        max_caffeine: searchParams.maxCaffeine === 400 ? undefined : searchParams.maxCaffeine,
        is_alcoholic: searchParams.isAlcoholic || undefined,
        excluded_ingredients: searchParams.excludedIngredients || undefined,
        page: 1,
        limit: 12,
      };

      // Filter out undefined values
      const filteredParams = Object.fromEntries(
        Object.entries(params).filter(([_, value]) => value !== undefined && value !== "")
      );

      navigate("/search?" + new URLSearchParams(filteredParams).toString());
    } catch (err) {
      console.error("Search error:", err);
      setError(err?.message || err?.error || "Failed to perform search.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 space-y-4">
      <h2 className="text-lg font-semibold">Advanced Drink Search</h2>
      <p className="text-sm text-slate-300">
        Find drinks that match your exact preferences and dietary needs.
      </p>

      {error && (
        <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-sm text-red-300">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-300 mb-1">Search Text</label>
            <input
              name="searchText"
              value={searchParams.searchText}
              onChange={handleChange}
              placeholder="e.g., latte, smoothie, mojito"
              className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">Category</label>
            <select
              name="category"
              value={searchParams.category}
              onChange={handleChange}
              className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="coffee">Coffee</option>
              <option value="tea">Tea</option>
              <option value="smoothie">Smoothie</option>
              <option value="alcohol">Alcoholic</option>
              <option value="juice">Juice</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-300 mb-1">Price Tier</label>
            <select
              name="priceTier"
              value={searchParams.priceTier}
              onChange={handleChange}
              className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any Price</option>
              <option value="$">Budget ($)</option>
              <option value="$$">Standard ($$)</option>
              <option value="$$$">Premium ($$$)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">
              Max Sweetness (1-10)
            </label>
            <input
              name="maxSweetness"
              type="range"
              min="1"
              max="10"
              value={searchParams.maxSweetness}
              onChange={handleChange}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>1</span>
              <span>5</span>
              <span>10</span>
            </div>
            <div className="text-center text-xs text-slate-300 mt-1">
              Current: {searchParams.maxSweetness}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-300 mb-1">
              Caffeine Range (mg)
            </label>
            <div className="flex gap-2">
              <input
                name="minCaffeine"
                type="number"
                min="0"
                max="400"
                value={searchParams.minCaffeine}
                onChange={handleChange}
                placeholder="Min"
                className="w-1/2 rounded-md bg-slate-900 border border-slate-700 px-2 py-1 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                name="maxCaffeine"
                type="number"
                min="0"
                max="400"
                value={searchParams.maxCaffeine}
                onChange={handleChange}
                placeholder="Max"
                className="w-1/2 rounded-md bg-slate-900 border border-slate-700 px-2 py-1 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              name="isAlcoholic"
              type="checkbox"
              checked={searchParams.isAlcoholic}
              onChange={handleChange}
              className="h-4 w-4 accent-purple-500 rounded"
              id="alcoholic-checkbox"
            />
            <label
              htmlFor="alcoholic-checkbox"
              className="ml-2 text-xs text-slate-300"
            >
              Alcoholic Drinks Only
            </label>
          </div>
        </div>

        <div>
          <label className="block text-xs text-slate-300 mb-1">
            Exclude Ingredients (comma-separated)
          </label>
          <input
            name="excludedIngredients"
            value={searchParams.excludedIngredients}
            onChange={handleChange}
            placeholder="e.g., dairy, nuts, gluten"
            className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
        >
          {loading ? "Searching…" : "Search Drinks"}
        </button>
      </form>
    </div>
  );
};

export default AdvancedSearch;
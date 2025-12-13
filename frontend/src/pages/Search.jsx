// src/pages/Search.jsx
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { axiosInstance } from "../utils/axiosHelper";
import CustomPagination from "../components/CustomPagnation";
import AdvancedSearch from "../components/AdvancedSearch";

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [drinks, setDrinks] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const limit = 12;

  const fetchDrinks = async (pageArg = 1) => {
    setLoading(true);
    setError("");

    try {
      // Convert search params to API params
      const apiParams = {
        search_text: searchParams.get("search_text") || undefined,
        category: searchParams.get("category") || undefined,
        price_tier: searchParams.get("price_tier") || undefined,
        max_sweetness: searchParams.get("max_sweetness") || undefined,
        min_caffeine: searchParams.get("min_caffeine") || undefined,
        max_caffeine: searchParams.get("max_caffeine") || undefined,
        is_alcoholic: searchParams.get("is_alcoholic") || undefined,
        excluded_ingredients: searchParams.get("excluded_ingredients") || undefined,
        page: pageArg,
        limit,
      };

      // Filter out undefined/empty values
      const filteredParams = Object.fromEntries(
        Object.entries(apiParams).filter(([_, value]) => value !== undefined && value !== "")
      );

      const response = await axiosInstance.get("/catalog/drinks", {
        params: filteredParams,
      });

      const data = response.data;
      setDrinks(data.drinks || []);
      setPage(data.page || pageArg);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error("Search error:", err);
      setError(err?.message || err?.error || "Failed to load search results.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrinks(1);
  }, [searchParams]);

  const handlePageChange = (newPage) => {
    fetchDrinks(newPage);
  };

  const getSearchDescription = () => {
    const params = [];
    
    if (searchParams.get("search_text")) {
      params.push(`"${searchParams.get("search_text")}"`);
    }
    
    if (searchParams.get("category")) {
      params.push(searchParams.get("category"));
    }
    
    if (searchParams.get("price_tier")) {
      params.push(searchParams.get("price_tier"));
    }
    
    if (searchParams.get("max_sweetness")) {
      params.push(`sweetness ≤ ${searchParams.get("max_sweetness")}`);
    }
    
    if (searchParams.get("is_alcoholic")) {
      params.push("alcoholic");
    }
    
    return params.length > 0 
      ? `Results for: ${params.join(", ")}`
      : "All Drinks";
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 text-white pt-4 pb-8">
      <div className="max-w-6xl mx-auto px-4 space-y-6">
        <section className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold">Search Results</h1>
              <p className="text-sm text-slate-300">{getSearchDescription()}</p>
            </div>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium transition-colors"
            >
              {showAdvanced ? "Hide Filters" : "Advanced Filters"}
            </button>
          </div>

          {showAdvanced && (
            <div className="space-y-4">
              <AdvancedSearch />
            </div>
          )}

          {loading && (
            <p className="text-sm text-slate-300">Loading results…</p>
          )}

          {error && (
            <p className="text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}

          {!loading && !error && drinks.length === 0 && (
            <p className="text-sm text-slate-400">
              No drinks found matching your criteria. Try adjusting your filters.
            </p>
          )}

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {drinks.map((drink) => (
              <Link
                key={drink.drink_id}
                to={`/drink/${drink.drink_id}`}
                className="rounded-xl bg-slate-900 border border-slate-700/70 p-4 hover:border-purple-500/60 hover:-translate-y-0.5 transition-all"
              >
                <h2 className="text-sm font-semibold mb-1">{drink.name}</h2>
                <p className="text-xs text-slate-400 mb-2 line-clamp-2">
                  {drink.description}
                </p>
                <div className="flex flex-wrap gap-2 text-[11px] text-slate-300">
                  {drink.category && (
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
                      {drink.category}
                    </span>
                  )}
                  <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
                    Sweetness {drink.sweetness_level}/10
                  </span>
                  {drink.price_tier && (
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
                      {drink.price_tier}
                    </span>
                  )}
                  {drink.is_alcoholic && (
                    <span className="px-2 py-0.5 rounded-full bg-red-900/60 border border-red-700">
                      {drink.alcohol_content}% ABV
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pt-4">
              <CustomPagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default SearchPage;
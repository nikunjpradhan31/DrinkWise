// src/pages/Landing.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { axiosInstance } from "../utils/axiosHelper";
import CustomPagination from "../components/CustomPagnation";
import AdvancedSearch from "../components/AdvancedSearch";
import PreferenceBasedRecommendations from "../components/PreferenceBasedRecommendations";
import InteractionBasedRecommendations from "../components/InteractionBasedRecommendations";

const LandingPage = () => {
  const [search, setSearch] = useState("");
  const [drinks, setDrinks] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const limit = 12;

  const fetchDrinks = async (pageArg = 1, searchArg = "") => {
    setLoading(true);
    setError("");
    try {
      const response = await axiosInstance.get("/catalog/drinks", {
        params: {
          search_text: searchArg || undefined,
          page: pageArg,
          limit,
        },
      });
      const data = response.data;
      setDrinks(data.drinks || []);
      setPage(data.page || pageArg);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error(err);
      setError(err?.message || err?.error || "Failed to load drinks.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrinks(1, "");
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchDrinks(1, search.trim());
  };

  const handlePageChange = (newPage) => {
    fetchDrinks(newPage, search.trim());
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 text-white pt-4 pb-8">
      <div className="max-w-6xl mx-auto px-4 space-y-6">
        <section className="space-y-4">
          <h1 className="text-2xl font-semibold">
            Discover your next favorite drink
          </h1>


          <form
            onSubmit={handleSubmit}
            className="flex flex-col sm:flex-row gap-3"
          >
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search drinks (e.g., caramel latte, green tea, berry smoothie)"
              className="flex-1 rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm font-medium"
            >
              Search
            </button>
          </form>
        </section>

        <section className="space-y-6">
          <AdvancedSearch />
        </section>

        <section className="space-y-6">
          <PreferenceBasedRecommendations />
        </section>

        <section className="space-y-6">
          <InteractionBasedRecommendations />
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Browse All Drinks</h2>
          <p className="text-sm text-slate-300">
            Explore our full catalog of beverages
          </p>

          {loading && (
            <p className="text-sm text-slate-300">Loading drinks…</p>
          )}
          {error && (
            <p className="text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}

          {!loading && !error && drinks.length === 0 && (
            <p className="text-sm text-slate-400">
              No drinks found. Try a different search.
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

export default LandingPage;

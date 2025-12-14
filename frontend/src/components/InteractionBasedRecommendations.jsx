// src/components/InteractionBasedRecommendations.jsx
import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { axiosInstance } from "../utils/axiosHelper";

const InteractionBasedRecommendations = () => {
  const { user } = useContext(AuthContext);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        // Fetch similar drinks based on user's favorites
        const response = await axiosInstance.get("/catalog/similar-user", {
          params: {
            limit: 6,
          },
        });

        setRecommendations(response.data.similar_drinks || []);
      } catch (err) {
        console.error("Error fetching interaction-based recommendations:", err);
        // If no favorites or similar drinks, that's okay - just show empty
        if (response?.status !== 404) {
          setError("Failed to load recommendations based on your interactions.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);
  if (!user) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Based on Your Favorites</h2>
        <p className="text-sm text-slate-300">
          Please log in to see drinks similar to your favorites.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Based on Your Favorites</h2>
        <p className="text-sm text-slate-300">Finding drinks similar to your favorites…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Based on Your Favorites</h2>
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Based on Your Favorites</h2>
        <p className="text-sm text-slate-300">
          Add some drinks to your favorites to get personalized recommendations!
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 space-y-4">
      <h2 className="text-lg font-semibold">Because You Liked These</h2>
      <p className="text-sm text-slate-300">
        Drinks similar to your favorites based on your taste profile
      </p>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.map((drink) => (
          <Link
            key={drink.drink.drink_id}
            to={`/drink/${drink.drink.drink_id}`}
            className="rounded-lg bg-slate-900 border border-slate-800 p-3 hover:border-purple-500/60 transition-all"
          >
            <p className="text-sm font-medium">{drink.drink.name}</p>
            <p className="text-xs text-slate-400 line-clamp-2 mt-1">
              {drink.drink.description}
            </p>
            <div className="text-[10px] text-slate-500 mt-1">
              {drink.drink.price_tier} • {drink.drink.category}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default InteractionBasedRecommendations;
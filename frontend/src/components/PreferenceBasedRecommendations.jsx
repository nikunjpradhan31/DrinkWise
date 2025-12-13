// src/components/PreferenceBasedRecommendations.jsx
import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { axiosInstance } from "../utils/axiosHelper";

const PreferenceBasedRecommendations = () => {
  const { user } = useContext(AuthContext);
  const [preferences, setPreferences] = useState(null);
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

        // Fetch user preferences
        const prefsResponse = await axiosInstance.get("/preferences");
        const prefsData = prefsResponse.data;
        setPreferences(prefsData);

        // Fetch drinks that match preferences
        const drinksResponse = await axiosInstance.get("/catalog/drinks", {
          params: {
            max_sweetness: prefsData.sweetness_preference, // Allow slightly sweeter
            max_caffeine: prefsData.caffeine_limit,
            price_tier: prefsData.preferred_price_tier,
            limit: 6,
          },
        });

        setRecommendations(drinksResponse.data.drinks || []);
      } catch (err) {
        console.error("Error fetching preference-based recommendations:", err);
        setError("Failed to load recommendations based on your preferences.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (!user) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Personalized Recommendations</h2>
        <p className="text-sm text-slate-300">
          Please log in to see drinks tailored to your taste preferences.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Personalized Recommendations</h2>
        <p className="text-sm text-slate-300">Loading drinks based on your preferences…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Personalized Recommendations</h2>
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Personalized Recommendations</h2>
        <p className="text-sm text-slate-300">
          No recommendations found based on your current preferences.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 space-y-4">
      <h2 className="text-lg font-semibold">Drinks Matching Your Taste</h2>
      <p className="text-sm text-slate-300">
        Based on your preferences: Sweetness {preferences?.sweetness_preference}/10, 
        Caffeine ≤ {preferences?.caffeine_limit}mg, {preferences?.preferred_price_tier} price tier
      </p>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.map((drink) => (
          <Link
            key={drink.drink_id}
            to={`/drink/${drink.drink_id}`}
            className="rounded-lg bg-slate-900 border border-slate-800 p-3 hover:border-green-500/60 transition-all"
          >
            <p className="text-sm font-medium">{drink.name}</p>
            <p className="text-xs text-slate-400 line-clamp-2 mt-1">
              {drink.description}
            </p>
            <div className="flex gap-2 text-[10px] text-slate-500 mt-2">
              <span>Sweetness: {drink.sweetness_level}/10</span>
              <span>Caffeine: {drink.caffeine_content}mg</span>
            </div>
            <div className="text-[10px] text-slate-500 mt-1">
              {drink.price_tier} • {drink.category}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default PreferenceBasedRecommendations;
// src/components/PreferenceComparison.jsx
import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { axiosInstance } from "../utils/axiosHelper";

const PreferenceComparison = ({ drink }) => {
  const { user } = useContext(AuthContext);
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPreferences = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const response = await axiosInstance.get("/preferences");
        setPreferences(response.data);
      } catch (err) {
        console.error("Error fetching preferences:", err);
        setError("Failed to load your preferences.");
      } finally {
        setLoading(false);
      }
    };

    fetchPreferences();
  }, [user]);

  if (!user) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Preference Comparison</h2>
        <p className="text-sm text-slate-300">
          Please log in to see how this drink matches your preferences.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Preference Comparison</h2>
        <p className="text-sm text-slate-300">Loading your preferences…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Preference Comparison</h2>
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Preference Comparison</h2>
        <p className="text-sm text-slate-300">
          You haven't set your preferences yet. Complete the taste quiz to see comparisons.
        </p>
      </div>
    );
  }

  // Calculate match scores
  const sweetnessMatch = Math.max(0, 100 - Math.abs(drink.sweetness_level - preferences.sweetness_preference) * 10);
  const caffeineMatch = drink.caffeine_content <= preferences.caffeine_limit ? 100 : 0;
  const priceMatch = drink.price_tier === preferences.preferred_price_tier ? 100 : 50;
  const overallMatch = Math.round((sweetnessMatch + caffeineMatch + priceMatch) / 3);

  return (
    <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 space-y-4">
      <h2 className="text-lg font-semibold">How This Drink Matches Your Preferences</h2>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-300">Overall Match:</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">{overallMatch}%</span>
            <div className="w-20 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500"
                style={{ width: `${overallMatch}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-300">Sweetness Match:</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">{sweetnessMatch}%</span>
            <div className="w-20 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500"
                style={{ width: `${sweetnessMatch}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-300">Caffeine Match:</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">{caffeineMatch}%</span>
            <div className="w-20 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-yellow-500"
                style={{ width: `${caffeineMatch}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-300">Price Tier Match:</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">{priceMatch}%</span>
            <div className="w-20 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500"
                style={{ width: `${priceMatch}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800">
        <h3 className="text-sm font-semibold mb-2">Detailed Comparison:</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Your Sweetness Pref:</span>
              <span className="font-medium">{preferences.sweetness_preference}/10</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Drink Sweetness:</span>
              <span className="font-medium">{drink.sweetness_level}/10</span>
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Your Caffeine Limit:</span>
              <span className="font-medium">{preferences.caffeine_limit}mg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Drink Caffeine:</span>
              <span className="font-medium">{drink.caffeine_content}mg</span>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-2 text-xs text-slate-400">
        {overallMatch >= 80 ? "🎯 Perfect match for your preferences!" : 
         overallMatch >= 60 ? "👍 Good match, you might enjoy this!" : 
         "⚠️ This drink may not fully match your preferences"}
      </div>
    </div>
  );
};

export default PreferenceComparison;
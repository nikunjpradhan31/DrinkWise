// src/components/PreferencePopup.jsx
import { useState, useEffect } from "react";
import { axiosInstance } from "../utils/axiosHelper";

const PreferencePopup = ({ isOpen, onClose, onSave }) => {
  const [preferences, setPreferences] = useState({
    sweetness_preference: 5,
    bitterness_preference: 5,
    caffeine_limit: 400,
    calorie_limit: 2000,
    preferred_price_tier: "$$"
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      const fetchPreferences = async () => {
        setLoading(true);
        setError("");
        try {
          const res = await axiosInstance.get("/preferences");
          const data = res.data;
          setPreferences({
            sweetness_preference: data.sweetness_preference || 5,
            bitterness_preference: data.bitterness_preference || 5,
            caffeine_limit: data.caffeine_limit || 400,
            calorie_limit: data.calorie_limit || 2000,
            preferred_price_tier: data.preferred_price_tier || "$$"
          });
        } catch (e) {
          console.error(e);
          // If no preferences exist yet, use defaults
          if (e.response && e.response.status !== 404) {
            setError(
              e?.message || e?.error || "Failed to load your preferences."
            );
          }
        } finally {
          setLoading(false);
        }
      };
      fetchPreferences();
    }
  }, [isOpen]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPreferences(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      // Update user preferences
      const res = await axiosInstance.put("/preferences", {
        sweetness_preference: parseInt(preferences.sweetness_preference),
        bitterness_preference: parseInt(preferences.bitterness_preference),
        caffeine_limit: parseInt(preferences.caffeine_limit),
        calorie_limit: parseInt(preferences.calorie_limit),
        preferred_price_tier: preferences.preferred_price_tier
      });

      const data = res.data;
      onSave?.(data);
      onClose();
    } catch (e) {
      console.error(e);
      setError(e?.message || e?.error || "Failed to save your preferences.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Update Your Preferences</h2>
          <button
            onClick={onClose}
            disabled={submitting}
            className="text-slate-400 hover:text-slate-200 disabled:opacity-50"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <p className="text-sm text-slate-300">Loading your preferences…</p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <p className="text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
                {error}
              </p>
            )}

            <p className="text-sm text-slate-300">
              Update your drink preferences to get better recommendations.
            </p>

            <div className="space-y-4">
              {/* Sweetness Preference */}
              <div className="rounded-lg bg-slate-800/50 p-3">
                <label className="text-sm font-medium text-white mb-2 block">
                  Sweetness Preference (1-10):
                </label>
                <input
                  type="range"
                  name="sweetness_preference"
                  min="1"
                  max="10"
                  value={preferences.sweetness_preference}
                  onChange={handleInputChange}
                  className="w-full accent-purple-500"
                />
                <span className="text-xs text-slate-200">{preferences.sweetness_preference}</span>
              </div>

              {/* Bitterness Preference */}
              <div className="rounded-lg bg-slate-800/50 p-3">
                <label className="text-sm font-medium text-white mb-2 block">
                  Bitterness Preference (1-10):
                </label>
                <input
                  type="range"
                  name="bitterness_preference"
                  min="1"
                  max="10"
                  value={preferences.bitterness_preference}
                  onChange={handleInputChange}
                  className="w-full accent-purple-500"
                />
                <span className="text-xs text-slate-200">{preferences.bitterness_preference}</span>
              </div>

              {/* Caffeine Limit */}
              <div className="rounded-lg bg-slate-800/50 p-3">
                <label className="text-sm font-medium text-white mb-2 block">
                  Daily Caffeine Limit (mg):
                </label>
                <input
                  type="number"
                  name="caffeine_limit"
                  min="0"
                  value={preferences.caffeine_limit}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white text-sm"
                />
              </div>

              {/* Calorie Limit */}
              <div className="rounded-lg bg-slate-800/50 p-3">
                <label className="text-sm font-medium text-white mb-2 block">
                  Daily Calorie Limit:
                </label>
                <input
                  type="number"
                  name="calorie_limit"
                  min="0"
                  value={preferences.calorie_limit}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white text-sm"
                />
              </div>

              {/* Price Tier */}
              <div className="rounded-lg bg-slate-800/50 p-3">
                <label className="text-sm font-medium text-white mb-2 block">
                  Preferred Price Tier:
                </label>
                <select
                  name="preferred_price_tier"
                  value={preferences.preferred_price_tier}
                  onChange={handleInputChange}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white text-sm"
                >
                  <option value="$">Budget ($)</option>
                  <option value="$$">Mid-range ($$)</option>
                  <option value="$$">Premium ($$$)</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                type="button"
                onClick={onClose}
                disabled={submitting}
                className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
              >
                {submitting ? "Saving…" : "Save Preferences"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default PreferencePopup;
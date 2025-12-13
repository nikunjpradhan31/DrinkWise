// src/pages/Account.jsx
import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { axiosInstance } from "../utils/axiosHelper";
import { AuthContext } from "../context/AuthContext";

const AccountPage = () => {
  const auth = useContext(AuthContext);
  const [prefs, setPrefs] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [recs, setRecs] = useState([]);
  const [stats, setStats] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  if (!auth) throw new Error("AuthContext missing");
  const { user, fetchMe } = auth;

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setErr("");
      try {
        await fetchMe();
        const [prefsRes, favRes, recRes, statsRes, interactionsRes] = await Promise.all([
          axiosInstance.get("/preferences"),
          axiosInstance.get("/user-drinks/favorites"),
          axiosInstance.get("/catalog/similar-user", {
            params: { limit: 6},
          }),
          axiosInstance.get("/auth/statistics"),
          axiosInstance.get("/user-drinks/statistics"),
        ]);
        setPrefs(prefsRes.data);
        setFavorites(favRes.data.favorites || []);
        setRecs(recRes.data.similar_drinks || []);
        setStats(statsRes.data);
        setInteractions(interactionsRes.data.interactions || []);
      } catch (e) {
        console.error(e);
        setErr(e?.message || e?.error || "Failed to load account data.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [fetchMe]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        Loading…
      </div>
    );
  }

  if (err || !user) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        {err || "Not logged in."}
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 text-white pt-4 pb-8">
      <div className="max-w-5xl mx-auto px-4 space-y-8">
        <section className="space-y-2">
          <h1 className="text-2xl font-semibold">My Account</h1>
          <p className="text-sm text-slate-300">
            Signed in as <span className="font-medium">{user.username}</span>
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 space-y-2">
            <h2 className="text-sm font-semibold mb-1">Profile</h2>
            <p className="text-xs text-slate-400">
              Joined:{" "}
              {user.joindate
                ? new Date(user.joindate).toLocaleDateString()
                : "—"}
            </p>
            <p className="text-xs text-slate-400">Email: {user.email}</p>
            {user.date_of_birth && (
              <p className="text-xs text-slate-400">
                Date of birth:{" "}
                {new Date(user.date_of_birth).toLocaleDateString()}
              </p>
            )}
            <p className="text-xs text-slate-400">
              Questionnaire finished:{" "}
              {user.preference_finished ? "Yes" : "No"}
            </p>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 space-y-2">
            <h2 className="text-sm font-semibold mb-1">Preferences</h2>
            {prefs ? (
              <ul className="text-xs text-slate-300 space-y-1">
                <li>Sweetness: {prefs.sweetness_preference}/10</li>
                <li>Bitterness: {prefs.bitterness_preference}/10</li>
                <li>Caffeine limit: {prefs.caffeine_limit} mg</li>
                <li>Calorie limit: {prefs.calorie_limit}</li>
                <li>Price tier: {prefs.preferred_price_tier}</li>
              </ul>
            ) : (
              <p className="text-xs text-slate-400">
                No preferences saved yet.
              </p>
            )}
          </div>
        </section>

        {stats && (
          <section className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 space-y-3">
            <h2 className="text-sm font-semibold">Your Drink Statistics</h2>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">Total Drinks Tried:</span>
                  <span className="font-medium">{stats.total_drinks_tried || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Favorite Drinks:</span>
                  <span className="font-medium">{stats.favorite_drinks_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Average Rating:</span>
                  <span className="font-medium">{(stats.average_rating || 0).toFixed(1)}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">Most Consumed:</span>
                  <span className="font-medium">{stats.most_consumed_drink || 'None'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Total Consumptions:</span>
                  <span className="font-medium">{stats.total_consumptions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Account Age:</span>
                  <span className="font-medium">{stats.account_age_days || 0} days</span>
                </div>
              </div>
            </div>
          </section>
        )}

        <section className="space-y-2">
          <h2 className="text-sm font-semibold">Favorite drinks</h2>
          {favorites.length === 0 ? (
            <p className="text-xs text-slate-400">
              You don&apos;t have any favorites yet.
            </p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {favorites.slice(0, 6).map((d) => (
                <Link
                  key={d.drink_id}
                  to={`/drink/${d.drink_id}`}
                  className="rounded-lg bg-slate-900 border border-slate-800 p-3 hover:border-blue-500/60 transition-all"
                >
                  <p className="text-sm font-medium">{d.name}</p>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                    {d.description}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </section>

        {interactions.length > 0 && (
          <section className="space-y-2">
            <h2 className="text-sm font-semibold">Recently Interacted Drinks</h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {interactions.slice(0, 6).map((interaction) => (
                <Link
                  key={interaction.drink_id}
                  to={`/drink/${interaction.drink_id}`}
                  className="rounded-lg bg-slate-900 border border-slate-800 p-3 hover:border-purple-500/60 transition-all"
                >
                  <p className="text-sm font-medium">{interaction.drink_name}</p>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                    {interaction.drink_description}
                  </p>
                  <div className="flex gap-2 text-[10px] text-slate-500 mt-2">
                    <span>⭐ {interaction.rating || 'Not rated'}</span>
                    <span>🍹 {interaction.times_consumed || 0}x</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
        <section className="space-y-2">
          <h2 className="text-sm font-semibold">Recommended for you</h2>
          {recs.length === 0 ? (
            <p className="text-xs text-slate-400">
              No recommendations yet. Try favoriting a few drinks!
            </p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
             {recs.map((d) => (
                <Link
                  key={d.drink.drink_id}
                  to={`/drink/${d.drink.drink_id}`}
                  className="rounded-lg bg-slate-900 border border-slate-700/80 p-3 hover:border-purple-500/60 transition-all"
                >
                  <p className="text-sm font-medium">{d.drink.name}</p>

                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                    {d.drink.description}
                  </p>


                  <div className="text-[10px] text-slate-500 mt-1">
                    {d.drink.price_tier} • {d.drink.category}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default AccountPage;

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
        const [prefsRes, favRes, recRes] = await Promise.all([
          axiosInstance.get("/preferences"),
          axiosInstance.get("/user-favorites"),
          axiosInstance.get("/recommendations/users", {
            params: { limit: 6, recommendation_type: "hybrid" },
          }),
        ]);

        setPrefs(prefsRes.data);
        setFavorites(favRes.data.favorites || []);
        setRecs(recRes.data.recommendations || []);
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
                <li>Sugar limit: {prefs.sugar_limit} g</li>
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

        <section className="space-y-2">
          <h2 className="text-sm font-semibold">Recommended for you</h2>
          {recs.length === 0 ? (
            <p className="text-xs text-slate-400">
              No recommendations yet. Try favoriting a few drinks!
            </p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {recs.map((r, idx) => (
                <Link
                  key={`${r.drink?.drink_id}-${idx}`}
                  to={`/drink/${r.drink.drink_id}`}
                  className="rounded-lg bg-slate-900 border border-slate-800 p-3 hover:border-blue-500/60 transition-all"
                >
                  <p className="text-sm font-medium">{r.drink.name}</p>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                    {r.drink.description}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-1">
                    Score: {(r.score * 100).toFixed(1)}%
                  </p>
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

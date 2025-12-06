// src/pages/DrinkPage.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { axiosInstance } from "../utils/axiosHelper";

const DrinkPage = () => {
  const { id } = useParams();
  const [drink, setDrink] = useState(null);
  const [interaction, setInteraction] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setErr("");
      try {
        const [drinkRes, interRes, simRes] = await Promise.all([
          axiosInstance.get(`/catalog/drinks/${id}`),
          axiosInstance.get(`/user-drinks/${id}`).catch(() => null),
          axiosInstance.get("/recommendations/drinks", {
            params: { drink_id: Number(id), limit: 6 },
          }),
        ]);

        setDrink(drinkRes.data);
        setInteraction(interRes?.data || null);
        setSimilar(simRes.data.similar_drinks || []);
      } catch (e) {
        console.error(e);
        setErr(e?.message || e?.error || "Failed to load drink.");
      } finally {
        setLoading(false);
      }
    };
    if (id) load();
  }, [id]);

  const updateInteraction = async (patch) => {
    try {
      const response = await axiosInstance.put(`/user-drinks/${id}`, patch);
      setInteraction(response.data);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        Loading…
      </div>
    );
  }

  if (err || !drink) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        {err || "Drink not found."}
      </div>
    );
  }

  const ingredients = drink.ingredients || [];
  const timesConsumed = interaction?.times_consumed ?? 0;
  const rating = interaction?.rating ?? 0;
  const isFavorite = interaction?.is_favorite ?? false;
  const isNotForMe = interaction?.is_not_for_me ?? false;

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 text-white pt-4 pb-8">
      <div className="max-w-4xl mx-auto px-4 space-y-8">
        <header className="space-y-3">
          <h1 className="text-2xl font-semibold">{drink.name}</h1>
          <p className="text-sm text-slate-300">{drink.description}</p>
          <div className="flex flex-wrap gap-2 text-[11px] text-slate-300">
            {drink.category && (
              <span className="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700">
                {drink.category}
              </span>
            )}
            <span className="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700">
              Sweetness {drink.sweetness_level}/10
            </span>
            <span className="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700">
              Caffeine {drink.caffeine_content} mg
            </span>
            <span className="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700">
              {drink.price_tier}
            </span>
            {drink.is_alcoholic && (
              <span className="px-2 py-0.5 rounded-full bg-red-900/60 border border-red-700">
                {drink.alcohol_content}% ABV
              </span>
            )}
          </div>
        </header>

        {ingredients.length > 0 && (
          <section className="space-y-2">
            <h2 className="text-sm font-semibold">Ingredients</h2>
            <ul className="text-sm text-slate-200 list-disc list-inside space-y-1">
              {ingredients.map((ing, idx) => (
                <li key={idx}>
                  {ing.quantity
                    ? `${ing.quantity} — ${ing.ingredient_name}`
                    : ing.ingredient_name}
                  {ing.is_allergen && (
                    <span className="ml-2 text-xs text-amber-400">
                      (allergen)
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="space-y-3 border-t border-slate-800 pt-4">
          <h2 className="text-sm font-semibold">Your rating</h2>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <button
              type="button"
              onClick={() =>
                updateInteraction({ is_favorite: !isFavorite })
              }
              className={`px-3 py-1 rounded-full border ${
                isFavorite
                  ? "border-blue-500 bg-blue-500/20 text-blue-100"
                  : "border-slate-600 bg-slate-900 text-slate-200"
              }`}
            >
              {isFavorite ? "★ Favorite" : "☆ Add to favorites"}
            </button>

            <button
              type="button"
              onClick={() =>
                updateInteraction({ times_consumed: timesConsumed + 1 })
              }
              className="px-3 py-1 rounded-full border border-slate-600 bg-slate-900 text-slate-200"
            >
              I made this ({timesConsumed})
            </button>

            <label className="flex items-center gap-2 text-xs text-slate-300">
              Rating (0–5):
              <input
                type="number"
                min={0}
                max={5}
                step={0.5}
                value={rating}
                onChange={(e) =>
                  updateInteraction({ rating: Number(e.target.value) || 0 })
                }
                className="w-16 px-2 py-1 bg-slate-900 border border-slate-700 rounded-md text-xs text-white"
              />
            </label>

            <button
              type="button"
              onClick={() =>
                updateInteraction({ is_not_for_me: !isNotForMe })
              }
              className={`px-3 py-1 rounded-full border text-xs ${
                isNotForMe
                  ? "border-amber-500 bg-amber-500/15 text-amber-200"
                  : "border-slate-600 bg-slate-900 text-slate-200"
              }`}
            >
              {isNotForMe ? "Marked as not for me" : "Not for me"}
            </button>
          </div>
        </section>

        {similar.length > 0 && (
          <section className="space-y-3 border-t border-slate-800 pt-4">
            <h2 className="text-sm font-semibold">Similar drinks</h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {similar.map((d) => (
                <Link
                  key={d.drink_id}
                  to={`/drink/${d.drink_id}`}
                  className="rounded-lg bg-slate-900 border border-slate-700/80 p-3 hover:border-purple-500/60 transition-all"
                >
                  <p className="text-sm font-medium">{d.name}</p>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                    {d.description}
                  </p>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default DrinkPage;

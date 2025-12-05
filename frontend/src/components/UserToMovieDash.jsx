import React, { useState, useEffect } from "react";
import { Heart, CheckCircle, PlayCircle } from "lucide-react";
import { useMovieContext } from "../context/MovieContext";

const UsertoMovieDash = ({ user, movie_id, info = {} }) => {
  const [timesWatched, setTimesWatched] = useState(info.times_watched ?? 0);
  const [hasWatched, setHasWatched] = useState(info.has_watched ?? false);
  const [isFavorite, setIsFavorite] = useState(info.is_favorite ?? false);
  const [watchingNow, setWatchingNow] = useState(info.watching_now ?? false);
  const [rating, setRating] = useState(info.rating ?? 0);

  const { updateUserToMovie } = useMovieContext();

  useEffect(() => {
    setTimesWatched(info.times_watched ?? 0);
    setHasWatched(info.has_watched ?? false);
    setIsFavorite(info.is_favorite ?? false);
    setWatchingNow(info.watching_now ?? false);
    setRating(info.rating ?? 0);
  }, [info]);

  const updateMovie = (updatedFields) => {
    updateUserToMovie(
      user.user_id,
      user.access_token,
      movie_id,
      updatedFields.timesWatched ?? timesWatched,
      updatedFields.hasWatched ?? hasWatched,
      updatedFields.isFavorite ?? isFavorite,
      updatedFields.watchingNow ?? watchingNow,
      updatedFields.rating ?? rating
    );
  };

  return (
    <div className="flex gap-6 justify-center items-center flex-nowrap overflow-auto">
      {/* Favorite */}
      <div className="flex items-center gap-2">
        <span className="text-purple-300 font-medium min-w-[60px] text-right">Favorite</span>
        <button
          type="button"
          onClick={() => {
            const newVal = !isFavorite;
            setIsFavorite(newVal);
            updateMovie({ isFavorite: newVal });
          }}
          className={`px-4 py-2 flex items-center justify-center rounded-full border transition-all duration-300 ${
            isFavorite
              ? "border-purple-500/50 bg-purple-500/10 text-purple-300"
              : "border-white/10 text-gray-400 hover:bg-white/10 hover:text-white"
          }`}
        >
          <Heart className="w-5 h-5" />
        </button>
      </div>

      {/* Watched */}
      <div className="flex items-center gap-2">
        <span className="text-purple-300 font-medium min-w-[60px] text-right">Watched</span>
        <button
          type="button"
          onClick={() => {
            const newVal = !hasWatched;
            setHasWatched(newVal);
            updateMovie({ hasWatched: newVal });
          }}
          className={`px-4 py-2 flex items-center justify-center rounded-full border transition-all duration-300 ${
            hasWatched
              ? "border-blue-500/50 bg-blue-500/10 text-blue-300"
              : "border-white/10 text-gray-400 hover:bg-white/10 hover:text-white"
          }`}
        >
          <CheckCircle className="w-5 h-5" />
        </button>
      </div>

      {/* Watching */}
      <div className="flex items-center gap-2">
        <span className="text-purple-300 font-medium min-w-[60px] text-right">Watching</span>
        <button
          type="button"
          onClick={() => {
            const newVal = !watchingNow;
            setWatchingNow(newVal);
            updateMovie({ watchingNow: newVal });
          }}
          className={`px-4 py-2 flex items-center justify-center rounded-full border transition-all duration-300 ${
            watchingNow
              ? "border-green-500/50 bg-green-500/10 text-green-300"
              : "border-white/10 text-gray-400 hover:bg-white/10 hover:text-white"
          }`}
        >
          <PlayCircle className="w-5 h-5" />
        </button>
      </div>

      {/* Rating */}
      <div className="flex items-center gap-2">
        <span className="text-purple-300 font-medium min-w-[60px] text-right">Rating</span>
        <input
          type="number"
          min={0}
          max={10}
          step={0.1}
          value={rating}
          onChange={(e) => {
            const val = parseFloat(e.target.value);
            setRating(val);
            updateMovie({ rating: val });
          }}
          className="w-20 px-2 py-1 rounded-md bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>

      {/* Times */}
      <div className="flex items-center gap-2">
        <span className="text-purple-300 font-medium min-w-[60px] text-right">Times Watched</span>
        <input
          type="number"
          min={0}
          value={timesWatched}
          onChange={(e) => {
            const val = parseInt(e.target.value);
            setTimesWatched(val);
            updateMovie({ timesWatched: val });
          }}
          className="w-20 px-2 py-1 rounded-md bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>
    </div>
  );
};

export default UsertoMovieDash;

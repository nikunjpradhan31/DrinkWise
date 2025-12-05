import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useMovieContext } from "../context/MovieContext";
import { Search, Filter, Calendar, Star, ChevronDown, ChevronUp } from 'lucide-react';



const SearchComponent = () => {
  const { getGenres } = useMovieContext();
const navigate = useNavigate()

  const [substring, setSubstring] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [releaseYear, setReleaseYear] = useState("");
  const [minRating, setMinRating] = useState("");
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [sortBy, setSortBy] = useState("rating");
  const [genres, setGenres] = useState([]);

  useEffect(() => {
    const fetchGenres = async () => {
      const genreList = await getGenres();
      setGenres(genreList);
    };

    fetchGenres();
  }, [getGenres]);

  const toggleGenre = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const params = new URLSearchParams();

    if (substring.trim()) params.append("substring", substring.trim());
    if (releaseYear) params.append("release_date", releaseYear);
    if (minRating) params.append("min_rating", minRating);
    if (selectedGenres.length > 0)
      selectedGenres.forEach((genre) => params.append("genres", genre));
    if (sortBy) params.append("sort_by", sortBy);

    params.append("page", "1");

    navigate(`/search-movies?${params.toString()}`);
  };


  return (
    <div className="w-full max-w-2xl mx-auto mb-8">
      {/* Main Search Form */}
      <div className="space-y-4">
        {/* Search Input Group */}
        <div className="flex gap-2">
          {/* Search Input */}
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search movies..."
              value={substring}
              onChange={(e) => setSubstring(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-black/20 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 hover:bg-black/30"
            />
          </div>

          {/* Filter Button */}
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-3 bg-black/20 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/30 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
            aria-label="Toggle filters"
          >
            <Filter className="w-5 h-5" />
            <span className="hidden sm:inline">Filter</span>
            {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {/* Search Button */}
          <button
            type="submit"
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold rounded-xl transition-all duration-200 transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-transparent shadow-lg shadow-purple-500/25"
            onClick={handleSubmit}
          >
            <Search className="w-5 h-5" />
            <span className="hidden sm:inline">Search</span>
          </button>
        </div>

        {/* Collapsible Filters */}
        {showFilters && (
  <div className="transition-all duration-300 ease-in-out opacity-100">

          <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl p-6 shadow-2xl space-y-6">
            {/* Release Year and Rating Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Release Year */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Release Year
                </label>
                <input
                  type="number"
                  min="1900"
                  max={new Date().getFullYear()}
                  value={releaseYear}
                  onChange={(e) => setReleaseYear(e.target.value)}
                  placeholder="e.g. 2023"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 hover:bg-white/10"
                />
              </div>

              {/* Minimum Rating */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <Star className="w-4 h-4" />
                  Minimum Rating
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(e.target.value)}
                  placeholder="e.g. 7.5"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 hover:bg-white/10"
                />
              </div>
            </div>

            {/* Genres */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-300">Genres</label>
              <div className="flex flex-wrap gap-2">
                {genres.length === 0 && (
                  <small className="text-gray-400">No genres available</small>
                )}
                {genres.map((genre) => (
                  <button
                    key={genre}
                    type="button"
                    onClick={() => toggleGenre(genre)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border select-none ${
                      selectedGenres.includes(genre)
                        ? 'bg-purple-500/20 text-purple-300 border-purple-500/50 shadow-lg shadow-purple-500/25'
                        : 'bg-white/5 text-gray-300 border-white/20 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort By */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 hover:bg-white/10 appearance-none cursor-pointer"
              >
                <option value="rating" className="bg-gray-800 text-white">Rating</option>
                <option value="release_year" className="bg-gray-800 text-white">Release Year</option>
              </select>
            </div>
          </div>
        </div>)}
      </div>
    </div>
  );
};

export default SearchComponent;
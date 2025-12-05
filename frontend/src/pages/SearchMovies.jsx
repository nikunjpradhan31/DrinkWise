import React, { useEffect,useState } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
// import { Container, Row, Col, Spinner, Alert, Card, Badge, Pagination } from "react-bootstrap";
import SearchComponent from "../components/SearchForMovie";
import CustomPagination from "../components/CustomPagnation";
import { useMovieContext } from "../context/MovieContext";

const SearchMoviesPage = () => {
  const [searchParams] = useSearchParams();
  const {
    fetchSearchedMovies,
    searchmovies,
    searchmoviesError,
    issearchmoviesLoading,
    totalPages
  } = useMovieContext();

  const getBadgeVariant = (rating) => {
    if (rating >= 7) return "success"; // Green
    if (rating >= 4) return "warning"; // Yellow
    return "danger"; // Red
  };

  // Helper function to get badge colors for glassmorphism design
  const getBadgeColors = (rating) => {
    const variant = getBadgeVariant(rating);
    switch (variant) {
      case "success":
        return "bg-green-500/20 text-green-300 border-green-500/30";
      case "warning":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
      case "danger":
        return "bg-red-500/20 text-red-300 border-red-500/30";
      default:
        return "bg-gray-500/20 text-gray-300 border-gray-500/30";
    }
  };

  const navigate = useNavigate();
  const currentPage = parseInt(searchParams.get("page") || "1");

  const handlePageChange = (pageNumber) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set("page", pageNumber);
    navigate(`/search-movies?${newParams.toString()}`);
  };

  useEffect(() => {
    const substring = searchParams.get("substring") || null;
    const release_date = searchParams.get("release_date") || null;
    const min_rating = searchParams.get("min_rating") || null;
    const sort_by = searchParams.get("sort_by") || "rating";
    const page = parseInt(searchParams.get("page") || "1");
     const genres = searchParams.getAll("genres");
    fetchSearchedMovies({
      substring,
      release_date,
      min_rating,
      genres,
      sort_by,
      page,
    });
  }, [searchParams, fetchSearchedMovies]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 pt-20">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-700/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/3 rounded-full blur-3xl"></div>
      </div>

      {/* Main Container */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Component */}
        <SearchComponent />

        {/* Header */}
        <div className="mb-8 mt-8">
          <h2 className="text-3xl font-bold text-white">Search Results</h2>
        </div>

        {/* Loading, Error, and Content */}
        {issearchmoviesLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
              <div className="flex items-center gap-4 text-white">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
                <span className="text-lg font-medium">Loading movies...</span>
              </div>
            </div>
          </div>
        ) : searchmoviesError ? (
          <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/20 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-3 text-red-400">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span className="font-medium">{searchmoviesError}</span>
            </div>
          </div>
        ) : searchmovies.length === 0 ? (
          <div className="text-center py-20">
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl inline-block">
              <p className="text-gray-400 text-lg">No movies found.</p>
            </div>
          </div>
        ) : (
          <>
            {/* Movies Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 mb-8">
              {searchmovies.map((movie, index) => (
                <div key={movie.movie_id || index} className="w-full">
                  {/* Glassmorphism Card */}
                  <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden hover:scale-105 transition-all duration-300 shadow-2xl hover:shadow-purple-500/25 group h-full flex flex-col">
                    <Link 
                      to={`/movie/${movie.movie_id}`} 
                      style={{ textDecoration: "none", color: "inherit" }}
                      className="flex flex-col h-full"
                    >
                      {/* Movie Image */}
                      <div className="relative overflow-hidden">
                        <img
                          src={movie.image_url || "https://via.placeholder.com/150"}
                          alt={movie.title}
                          className="w-full h-80 object-cover group-hover:scale-110 transition-transform duration-500"
                          style={{ height: "300px", objectFit: "cover" }}
                        />
                        {/* Overlay gradient for better text readability */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        
                        {/* Rating Badge - top right corner */}
                        <div className="absolute top-3 right-3">
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-medium border flex-shrink-0 ${getBadgeColors(movie.rating)}`}
                            style={{ minWidth: "35px", textAlign: "center" }}
                          >
                            {movie.rating || "N/A"}
                          </span>
                        </div>
                      </div>
                      
                      {/* Card Body - Movie Title at bottom */}
                      <div className="p-4 flex-grow flex items-end">
                        <h5 
                          className="text-white font-semibold group-hover:text-purple-300 transition-colors w-full"
                          style={{ 
                            fontSize: "1rem", 
                            whiteSpace: "nowrap", 
                            overflow: "hidden", 
                            textOverflow: "ellipsis" 
                          }}
                        >
                          {movie.title}
                        </h5>
                      </div>
                    </Link>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex justify-center mt-12">
              <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-2 shadow-2xl">
                <CustomPagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  handlePageChange={handlePageChange}
                />
              </div>
            </div>
          </>
        )}

        {/* Custom scrollbar styles */}
        <style jsx>{`
          .scrollbar-hide {
            -ms-overflow-style: none;
            scrollbar-width: none;
          }
          .scrollbar-hide::-webkit-scrollbar {
            display: none;
          }
        `}</style>
      </div>
    </div>
  );
};

export default SearchMoviesPage;
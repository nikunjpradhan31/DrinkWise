import React, { useEffect } from "react";
import { useMovieContext } from "../context/MovieContext";
import { Search, Loader2, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';

import { Link } from "react-router-dom";
import HorizontalMovieRow from "../components/HorizontalMovieRow"
import SearchComponent from "../components/SearchForMovie";
const MoviesPage = () => {
  const { movies, fetchMovies, updateSearchInfo, searchInfo, getMovieError, isMovieGettingLoading } =
    useMovieContext();
  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  // const handleSearchChange = (e) => {
  //   updateSearchInfo({ ...searchInfo, substring: e.target.value, page: 1 });
  // };

  // const handleNextPage = () => {
  //   updateSearchInfo({ ...searchInfo, page: searchInfo.page + 1 });
  // };

  // const handlePreviousPage = () => {
  //   updateSearchInfo({ ...searchInfo, page: Math.max(searchInfo.page - 1, 1) });
  // };





// const HorizontalMovieRow = ({ title, movies }) => (
//   <div className="mb-5">
//     <h4 className="mb-3">{title}</h4>
//     {movies && movies.length > 0 ? (
//       <div style={{ display: "flex", overflowX: "auto", gap: "1rem", paddingBottom: "0.5rem" }}>
//         {movies.map((movie, index) => (
//           <div
//             key={movie.movie_id || index}
//             style={{ minWidth: "200px", flex: "0 0 auto" }}
//           >
//             <Card>
//               <Link to={`/movie/${movie.movie_id}`} style={{ textDecoration: "none", color: "inherit" }}>
//                 <Card.Img
//                   variant="top"
//                   src={movie.image_url || "https://via.placeholder.com/150"}
//                   style={{ height: "300px", objectFit: "cover" }}
//                 />
//                 <Card.Body className="d-flex justify-content-between align-items-center">
//                   <Card.Title className="mb-0" style={{ fontSize: "1rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
//                     {movie.title}
//                   </Card.Title>
//                   <Badge
//                     pill
//                     bg={getBadgeVariant(movie.rating)}
//                     className="fs-6"
//                     style={{ minWidth: "35px", textAlign: "center" }}
//                   >
//                     {movie.rating || "N/A"}
//                   </Badge>
//                 </Card.Body>
//               </Link>
//             </Card>
//           </div>
//         ))}
//       </div>
//     ) : (
//       <p className="text-muted">No movies to display.</p>
//     )}
//   </div>
// );

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
        {/* Search Component - your exact component */}
        <SearchComponent />

        {/* Loading, Error, and Content - your exact logic */}
        {isMovieGettingLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
              <div className="flex items-center gap-4 text-white">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
                <span className="text-lg font-medium">Loading movies...</span>
              </div>
            </div>
          </div>
        ) : getMovieError ? (
          <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/20 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-3 text-red-400">
              <AlertCircle className="w-6 h-6" />
              <span className="font-medium">{getMovieError}</span>
            </div>
          </div>
        ) : (
          <>
            {movies ? (
              <>
                {/* Your exact HorizontalMovieRow components */}
                <HorizontalMovieRow title="Movies Recommended for You" movies={movies?.recommended_movies} />
                {movies?.collaborative_movies && movies?.collaborative_movies?.length > 4 && (   <HorizontalMovieRow title="Movies Similar Users Liked" movies={movies?.collaborative_movies} />)}
              
                {/* <HorizontalMovieRow title="Latest Movies" movies={movies?.new_movies} /> */}
                <HorizontalMovieRow title="Popular Movies" movies={movies?.popular_movies} />
                {movies?.unreleased_movies && movies?.unreleased_movies?.length > 4 && ( <HorizontalMovieRow title="Unreleased Movies" movies={movies?.unreleased_movies} />)}
              </>
            ) : (
              <div className="text-center py-20">
                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl inline-block">
                  <p className="text-gray-400 text-lg">No movies available</p>
                </div>
              </div>
            )}
          </>
        )}

        {/* Pagination (commented out in your code, but styled for consistency) */}
        {/* <div className="flex justify-center mt-12">
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-2 shadow-2xl">
            <div className="flex items-center gap-2">
              <button
                onClick={handlePreviousPage}
                disabled={searchInfo.page === 1}
                className="flex items-center gap-2 px-4 py-2 text-white hover:bg-white/10 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
              <div className="px-4 py-2 bg-purple-500/20 text-purple-300 rounded-xl font-medium border border-purple-500/30">
                {searchInfo.page}
              </div>
              <button
                onClick={handleNextPage}
                className="flex items-center gap-2 px-4 py-2 text-white hover:bg-white/10 rounded-xl transition-all duration-200"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div> */}
      </div>

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
  );
};

export default MoviesPage;

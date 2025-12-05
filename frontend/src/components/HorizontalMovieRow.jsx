// import { Container, Row, Col, Form, Button, Spinner, Alert, Card, Pagination, Badge } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useState } from "react";

// Your exact getBadgeVariant function - unchanged
const getBadgeVariant = (rating) => {
  if (rating >= 7) return "success"; // Green
  if (rating >= 4) return "warning"; // Yellow
  return "danger"; // Red
};

const HorizontalMovieRow = ({ title, movies }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const itemsPerPage = 6; // Number of movies to show at once

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

  const handlePrevious = () => {
    setCurrentIndex(Math.max(0, currentIndex - itemsPerPage));
  };

  const handleNext = () => {
    setCurrentIndex(Math.min(movies.length - itemsPerPage, currentIndex + itemsPerPage));
  };

  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex + itemsPerPage < movies.length;

  return (
    <div className="mb-8">
      {/* Your exact title - unchanged */}
      <h4 className="mb-6 text-2xl font-bold text-white px-2">{title}</h4>
      
      {/* Your exact conditional rendering logic - unchanged */}
      {movies && movies.length > 0 ? (
        <div className="relative flex items-center">
          {/* Navigation Arrows */}
          <div className="absolute left-0 top-1/2 -translate-y-1/2 z-10">
            {canGoPrevious ? (
              <button
                onClick={handlePrevious}
                className="bg-black/50 backdrop-blur-sm border border-white/20 rounded-full p-3 text-white hover:bg-black/70 transition-all duration-300 hover:scale-110"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            ) : (
              <div className="w-12 h-12"></div>
            )}
          </div>
          
          <div className="absolute right-0 top-1/2 -translate-y-1/2 z-10">
            {canGoNext ? (
              <button
                onClick={handleNext}
                className="bg-black/50 backdrop-blur-sm border border-white/20 rounded-full p-3 text-white hover:bg-black/70 transition-all duration-300 hover:scale-110"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ) : (
              <div className="w-12 h-12"></div>
            )}
          </div>

          <div className="flex gap-4 pb-4 px-16 mx-auto justify-center w-full">
            {/* Your exact map function and key logic - unchanged */}
            {movies.slice(currentIndex, currentIndex + itemsPerPage).map((movie, index) => (
              <div
                key={movie.movie_id || (currentIndex + index)}
                className="flex-shrink-0 w-52" // Fixed width for uniform card sizes
              >
                {/* Glassmorphism Card */}
                <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden hover:scale-105 transition-all duration-300 shadow-2xl hover:shadow-purple-500/25 group h-full flex flex-col">
                  {/* Your exact Link component with same props - unchanged */}
                  <Link 
                    to={`/movie/${movie.movie_id}`} 
                    style={{ textDecoration: "none", color: "inherit" }}
                    className="flex flex-col h-full"
                  >
                    {/* Movie Image - your exact src and placeholder logic - unchanged */}
                    <div className="relative overflow-hidden">
                      <img
                        src={movie.image_url || "https://via.placeholder.com/150"}
                        alt={movie.title}
                        className="w-full h-80 object-cover group-hover:scale-110 transition-transform duration-500"
                        style={{ height: "300px", objectFit: "cover" }} // Your exact inline styles
                      />
                      {/* Overlay gradient for better text readability */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      
                      {/* Rating Badge - moved to top right corner */}
                      <div className="absolute top-3 right-3">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium border flex-shrink-0 ${getBadgeColors(movie.rating)}`}
                          style={{ minWidth: "35px", textAlign: "center" }} // Your exact inline styles
                        >
                          {movie.rating || "N/A"}
                        </span>
                      </div>
                    </div>
                    
                    {/* Card Body - Movie Title moved to bottom */}
                    <div className="p-4 flex-grow flex items-end">
                      {/* Movie Title - your exact styling and overflow logic - unchanged */}
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
        </div>
      ) : (
        /* Your exact no movies message - unchanged */
        <div className="px-2">
          <p className="text-gray-400 text-lg">No movies to display.</p>
        </div>
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
  );
};

export default HorizontalMovieRow;
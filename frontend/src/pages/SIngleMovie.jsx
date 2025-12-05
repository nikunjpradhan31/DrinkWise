import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  useMovieContext,
} from "../context/MovieContext";
import { useAuthContext } from "../context/AuthContext";
import UsertoMovieDash from "../components/UserToMovieDash";
import HorizontalMovieRow from "../components/HorizontalMovieRow";
import { Star, Calendar, Clock, User, Users, Plus, X, Send, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

const MovieDetailsPage = () => {
  const { user,fetchFriends,friends } = useAuthContext();
  const { id } = useParams();
  const {
    getMovieError,
    fetchUserWatchlists,
    watchlists,
    addMovieToWatchlist,
    getSingleMovie,
    createRecommendation,getUserToMovieInfo, getMovieRecommendations, getGuestWatchlists,
    guest_watchlists,
  } = useMovieContext();
  const [movie, setMovie] = useState(null);
  
  const [combined_watchlists, set_combined_watchlists] = useState([])
  const [message, setMessage] = useState(null);
  const [isLoading, setisLoading] = useState(false)
  const [showRecommendModal, setShowRecommendModal] = useState(false);
  const [showWatchListModel, setShowWatchListModel] = useState(false)
  const[user_to_movie_info, set_user_to_movie_info] = useState({})
  const [movie_recommendations, set_movie_recommendations] = useState([])
  
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

  useEffect(() => {
    if (user) fetchFriends();
}, [user, fetchFriends]);

useEffect(() => {
  const fetchMovie = async () => {
    try {
      setisLoading(true);
      const singleMovie = await getSingleMovie(Number(id));
      const info = await getUserToMovieInfo(user?.user_id, user?.access_token, id);
      const recommendations = await getMovieRecommendations(id);
      set_movie_recommendations(recommendations);
      setMovie(singleMovie);
      set_user_to_movie_info(info);
      setMessage(null)
    } catch (error) {
      console.error("Failed to fetch movie:", error);
    } finally {
      setisLoading(false);
    }
  };

  if (user) {
    fetchMovie();
  }
}, [user, id, getSingleMovie]);


  useEffect(() => {
    if (user){
    fetchUserWatchlists();
    getGuestWatchlists(user.user_id, user.access_token);}
  }, [user , fetchUserWatchlists]);

useEffect(() => {
  const combined = [
    ...(watchlists ?? []),
    ...(guest_watchlists?.filter(wl => wl.role === "Editor") ?? []),
  ];
  set_combined_watchlists(combined);
}, [watchlists, guest_watchlists]);

const handleAddToWatchlist = async (watchlistId) => {
  if (watchlistId && movie) {
    const watchlist = combined_watchlists.find(
      (wl) => wl.watchlist_id === Number(watchlistId)
    );
    try {
      const res = await addMovieToWatchlist(watchlistId, movie.movie_id);

      if (res === 204)
        setMessage({
          type: "success",
          text: `"${movie.title}" is already in ${watchlist.watchlist_title}!`,
        });
      else
        setMessage({
          type: "success",
          text: `"${movie.title}" is in ${watchlist.watchlist_title}!`,
        });
    } catch (err) {
      setMessage({
        type: "error",
        text: `"Unable to add ${movie.title}" to ${watchlist.watchlist_title}!`,
      });
    }
  }
};


  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 flex items-center justify-center">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center gap-4 text-white">
            <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
            <span className="text-lg font-medium">Loading movie details...</span>
          </div>
        </div>
      </div>
    );
  }

  if (getMovieError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 flex items-center justify-center p-4">
        <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/20 rounded-2xl p-6 shadow-2xl max-w-md w-full">
          <div className="flex items-center gap-3 text-red-400">
            <AlertCircle className="w-6 h-6" />
            <span className="font-medium">{getMovieError}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 flex items-center justify-center p-4">
        <div className="bg-yellow-500/10 backdrop-blur-xl border border-yellow-500/20 rounded-2xl p-6 shadow-2xl max-w-md w-full">
          <div className="flex items-center gap-3 text-yellow-400">
            <AlertCircle className="w-6 h-6" />
            <span className="font-medium">Movie not found!</span>
          </div>
        </div>
      </div>
    );
  }

  const handleRecommend = async (friendUsername) => {
    if (!movie) return;

    try {
      await createRecommendation(movie.movie_id, friendUsername, user.access_token);
      let friend_user = friends?.find((friend)=>friend.user_id == friendUsername)
      setMessage({text: `Recommendation sent to ${friend_user?.username}!`, type: "success"});
      setShowRecommendModal(false)
    } catch (error) {
      let friend_user = friends?.find((friend)=>friend.user_id == friendUsername)
      setMessage({text: `You have already recommended "${movie.title}" to ${friend_user?.username}!`, type: "error"});

    }
  };

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
        {/* Movie Details Card */}
        <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 p-8">
            {/* Movie Poster */}
            <div className="lg:col-span-1 flex justify-center">
              <div className="relative group">
                <img
                  src={movie.image_url || "https://via.placeholder.com/300"}
                  alt={movie.title}
                  className="w-full max-w-sm rounded-2xl shadow-2xl group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            </div>

            {/* Movie Information */}
            <div className="lg:col-span-2 space-y-6">
              {/* Title and Rating */}
              <div className="space-y-4">
                <h1 className="text-4xl font-bold text-white">{movie.title}</h1>
                <div className="flex items-center gap-3">
                  <Star className="w-6 h-6 text-yellow-400" />
                  <span
                    className={`px-4 py-2 rounded-full text-lg font-medium border ${getBadgeColors(movie.rating)}`}
                  >
                    {movie.rating}
                  </span>
                </div>
              </div>

              {/* Movie Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-300">
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-purple-400 mt-1 flex-shrink-0" />
                    <div>
                      <span className="text-purple-300 font-medium">Director:</span>
                      <p className="text-white">{movie.director || "Unknown"}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <Users className="w-5 h-5 text-purple-400 mt-1 flex-shrink-0" />
                    <div>
                      <span className="text-purple-300 font-medium">Actors:</span>
                      <p className="text-white">{movie.actors?.join(", ") || "Unknown"}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-purple-400 mt-1 flex-shrink-0" />
                    <div>
                      <span className="text-purple-300 font-medium">Length:</span>
                      <p className="text-white">{movie.movie_length ? `${movie.movie_length} min` : "Unknown"}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-purple-400 mt-1 flex-shrink-0" />
                    <div>
                      <span className="text-purple-300 font-medium">Release Date:</span>
                      <p className="text-white">
                        {movie.release_date
                          ? new Date(movie.release_date).toLocaleDateString()
                          : "Unknown"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Genres */}
              <div>
                <span className="text-purple-300 font-medium">Genres:</span>
                <div className="flex flex-wrap gap-2 mt-2">
                  {movie.genres?.map((genre, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full text-sm"
                    >
                      {genre}
                    </span>
                  )) || <span className="text-white">Unknown</span>}
                </div>
              </div>

              {/* Description */}
              <div>
                <span className="text-purple-300 font-medium">Description:</span>
                <p className="text-gray-300 mt-2 leading-relaxed">
                  {movie.description || "No description available."}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-4 pt-4">
                <button
                  onClick={() => setShowRecommendModal(true)}
                  className="flex items-center gap-2 px-6 py-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 rounded-lg transition-all duration-300 hover:scale-105"
                >
                  <Send className="w-4 h-4" />
                  Recommend to Friends
                </button>
                
                <button
                  onClick={() => setShowWatchListModel(true)}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 rounded-lg transition-all duration-300 hover:scale-105"
                >
                  <Plus className="w-4 h-4" />
                  Add to Watchlist
                </button>
                
              </div>

              {/* Message Alert */}
              {message && (
                <div className={`flex items-center gap-3 p-4 rounded-lg border ${
                  message.type === "success" 
                    ? "bg-green-500/10 border-green-500/20 text-green-400" 
                    : "bg-red-500/10 border-red-500/20 text-red-400"
                }`}>
                  {message.type === "success" ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <AlertCircle className="w-5 h-5" />
                  )}
                  <span>{message.text}</span>
                </div>
              )}
            </div>
           
          </div>
           
 {user && (
          <div className="mb-8">
            <UsertoMovieDash
              user={user}
              movie_id={id}
              info={user_to_movie_info || {}}
            />
          </div>
        )}
        </div>

        {/* User to Movie Dashboard */}
       
        {/* Similar Movies */}
        {movie_recommendations && movie_recommendations.length > 0 ? (
          <HorizontalMovieRow title="Similar to this" movies={movie_recommendations} />
        ) : (
          <p className="text-gray-400 text-lg px-2">No similar movies found.</p>
        )}
      </div>

      {/* Recommendation Modal */}
      {showRecommendModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white">Recommend Movie to Friends</h3>
                <button
                  onClick={() => setShowRecommendModal(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>
            
            <div className="p-6 max-h-96 overflow-y-auto">
              {friends?.length && friends?.length > 0 && friends ? (
                <div className="space-y-3">
                  {friends.map((friend) => (
                    <div key={friend.username} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                      <span className="text-white font-medium">{friend.username}</span>
                      <button
                        onClick={() => handleRecommend(friend.user_id)}
                        className="px-4 py-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 rounded-lg transition-all duration-300 hover:scale-105"
                      >
                        Recommend
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-3 text-blue-400">
                    <AlertCircle className="w-5 h-5" />
                    <span>You have no friends to recommend to.</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Watchlist Modal */}
      {showWatchListModel && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white">Add Movie to Watchlist</h3>
                <button
                  onClick={() => setShowWatchListModel(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>
            
            <div className="p-6 max-h-96 overflow-y-auto">
              {combined_watchlists && combined_watchlists?.length > 0 ? (
                <div className="space-y-3">
                  {combined_watchlists.map((watchlist) => (
                    <div key={watchlist.watchlist_title} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                      <span className="text-white font-medium">{watchlist.watchlist_title}</span>
                      <button
                        onClick={() => {handleAddToWatchlist(watchlist.watchlist_id)}}
                        className="p-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 rounded-lg transition-all duration-300 hover:scale-105"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-3 text-blue-400">
                    <AlertCircle className="w-5 h-5" />
                    <span>You do not have any watchlists.</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MovieDetailsPage;
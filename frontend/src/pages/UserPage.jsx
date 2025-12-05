import React, { useState, useEffect, useContext } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Loader2, AlertCircle, User, Star, Eye, Clock, Award, Calendar, Edit3, Users } from 'lucide-react';

const UserPage = () => {
  const { user_id } = useParams(); 
  const { user, userMovieActions, fetchUserMovieActions, isLoadingActions, actionsError, fetchFriends } = useContext(AuthContext);
  const [profileUser, setProfileUser] = useState(null);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [isFriend, setIsFriend] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const checkUserAccess = async () => {
      setIsLoading(true);
      
      // If no user_id in params, show current user's profile
      if (!Number(user_id)) {
        if (user) {
          setProfileUser(user);
          setIsOwnProfile(true);
          setIsFriend(false);
          setAccessDenied(false);
          await fetchUserMovieActions(user);
        } else {
          setAccessDenied(true);
        }
        setIsLoading(false);
        return;
      }

      // If user_id matches current user, show own profile
      if (user && user.user_id === Number(user_id)) {
        setProfileUser(user);
        setIsOwnProfile(true);
        setIsFriend(false);
        setAccessDenied(false);
        await fetchUserMovieActions(user);
        setIsLoading(false);
        return;
      }
      // Check if user is logged in
      if (!user) {
        setAccessDenied(true);
        setIsLoading(false);
        return;
      }

      // Fetch friends and check if user_id is a friend
      const friends = await fetchFriends();
      const friendUser = friends && friends?.find(friend => friend.user_id === Number(user_id));
      if (friendUser) {
        setProfileUser(friendUser);
        setIsOwnProfile(false);
        setIsFriend(true);
        setAccessDenied(false);
        await fetchUserMovieActions(friendUser);
      } else {
        // User is not a friend - deny access
        setAccessDenied(true);
      }
      
      setIsLoading(false);
    };

    checkUserAccess();
  }, [user_id, user]);

  // Process movie data for different categories
  const processMovieData = () => {
    if (!userMovieActions) return { favorites: [], watched: [], currentlyWatching: [], analytics: {} };

    const favorites = userMovieActions.filter(item => item.user_action.is_favorite);
    const watched = userMovieActions.filter(item => item.user_action.has_watched);
    const currentlyWatching = userMovieActions.filter(item => item.user_action.watching_now);
    
    // Calculate highest rated movies
    const ratedMovies = userMovieActions.filter(item => item.user_action.rating > 0);
    const highestRated = ratedMovies.sort((a, b) => b.user_action.rating - a.user_action.rating).slice(0, 5);
    
    // Calculate favorite genres
    const genreCount = {};
    userMovieActions.forEach(item => {
      if (item.user_action.has_watched || item.user_action.is_favorite) {
        item.movie.genres.forEach(genre => {
          genreCount[genre] = (genreCount[genre] || 0) + 1;
        });
      }
    });
    
    const favoriteGenres = Object.entries(genreCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([genre]) => genre);

    const analytics = {
      totalFavorites: favorites.length,
      totalWatched: watched.length,
      currentlyWatching: currentlyWatching.length,
      highestRated: highestRated,
      favoriteGenres: favoriteGenres,
      totalMoviesInteracted: userMovieActions.length,
      currentlyWatchingMovies: currentlyWatching
    };

    return { favorites, watched, currentlyWatching, analytics };
  };

  const { favorites, watched, currentlyWatching, analytics } = processMovieData();

  const MovieCard = ({ movie, userAction }) => (
    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl min-w-[350px] mr-6 hover:bg-black/50 transition-all duration-300 hover:scale-105">
      <Link to={`/movie/${movie.movie_id}`} className="block">
        <div className="flex">
          <img
            src={movie.image_url}
            alt={movie.title}
            className="w-32 h-48 object-cover rounded-l-2xl"
          />
          <div className="flex flex-col p-6 flex-1">
            <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2">{movie.title}</h3>
            <p className="text-gray-400 text-sm mb-2">
              <span className="font-medium">Rating:</span> {movie.rating}/10
            </p>
            {userAction.rating > 0 && (
              <p className="text-purple-300 text-sm mb-2">
                <span className="font-medium">{isOwnProfile ? 'Your' : 'Their'} Rating:</span> {userAction.rating}/10
              </p>
            )}
            <div className="flex flex-wrap gap-2 mb-2">
              {movie.genres.slice(0, 2).map((genre, index) => (
                <span key={index} className="bg-gray-700/50 text-gray-300 px-2 py-1 rounded text-xs">
                  {genre}
                </span>
              ))}
            </div>
            {userAction.times_watched > 1 && (
              <span className="inline-flex items-center px-3 py-1 text-sm font-medium bg-purple-500/20 text-purple-300 rounded-lg border border-purple-500/30 self-start mt-auto">
                Watched {userAction.times_watched}x
              </span>
            )}
          </div>
        </div>
      </Link>
    </div>
  );

  const HorizontalMovieList = ({ title, movies, emptyMessage }) => (
    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl mb-8">
      <div className="p-6 border-b border-white/10">
        <h2 className="text-white text-2xl font-semibold mb-0">{title} ({movies.length})</h2>
      </div>
      <div className="p-6">
        {movies.length > 0 ? (
          <div className="flex overflow-x-auto pb-4 scrollbar-hide" style={{ scrollbarWidth: 'thin' }}>
            {movies.map((item) => (
              <MovieCard 
                key={item.movie.movie_id} 
                movie={item.movie} 
                userAction={item.user_action}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-lg mb-0">{emptyMessage}</p>
        )}
      </div>
    </div>
  );

  // Loading state
  if (isLoading || isLoadingActions) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 pt-20">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-700/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="relative z-10 flex items-center justify-center py-20">
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
            <div className="flex items-center gap-4 text-white">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
              <span className="text-lg font-medium">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (actionsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 pt-20">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-700/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/20 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-3 text-red-400">
              <AlertCircle className="w-6 h-6" />
              <span className="font-medium">{actionsError}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Access denied state
  if (accessDenied) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 pt-20">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-700/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-amber-500/10 backdrop-blur-xl border border-amber-500/20 rounded-2xl p-8 shadow-2xl">
            <div className="flex items-start gap-4">
              <AlertCircle className="w-8 h-8 text-amber-400 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-amber-300 text-xl font-semibold mb-3">Access Denied</h2>
                <p className="text-amber-100 mb-4">
                  {!user 
                    ? "You need to be logged in to view user profiles."
                    : Number(user_id) 
                      ? "You can only view profiles of users who are your friends."
                      : "User profile not found."
                  }
                </p>
                {!user && (
                  <Link
                    to="/"
                    className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-xl transition-colors duration-200"
                  >
                    Login
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // User not found state
  if (!profileUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900 pt-20">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-700/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-amber-500/10 backdrop-blur-xl border border-amber-500/20 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-400">
              <AlertCircle className="w-6 h-6" />
              <span className="font-medium">User not found</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main profile content
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
        {/* Combined User Profile and Stats Card */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl mb-8">
          <div className="p-8">
            <div className="flex flex-col lg:flex-row gap-8">
              {/* User Info Section */}
              <div className="flex flex-col lg:flex-row items-center lg:items-start gap-6 lg:min-w-0 lg:flex-shrink-0">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-12 h-12 text-white" />
                </div>
                <div className="text-center lg:text-left">
                  <div className="flex items-center justify-center lg:justify-start gap-3 mb-2">
                    <h1 className="text-white text-3xl font-bold">{profileUser.username}</h1>
                    {isFriend && (
                      <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium bg-green-500/20 text-green-300 rounded-lg border border-green-500/30">
                        <Users className="w-3 h-3" />
                        Friend
                      </span>
                    )}
                  </div>
                  {isOwnProfile && (
                    <p className="text-gray-400 mb-2">{profileUser.email}</p>
                  )}
                  {profileUser.description && (
                    <p className="text-gray-300 mb-3 max-w-md">{profileUser.description}</p>
                  )}
                  <div className="flex items-center justify-center lg:justify-start gap-2 text-gray-400 text-sm">
                    <Calendar className="w-4 h-4" />
                    <span>Joined {new Date(profileUser.joindate).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="w-4 h-4 text-purple-400" />
                    <span className="text-gray-400 text-sm">Favorites</span>
                  </div>
                  <p className="text-white text-2xl font-bold">{analytics.totalFavorites}</p>
                </div>
                <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="w-4 h-4 text-green-400" />
                    <span className="text-gray-400 text-sm">Watched</span>
                  </div>
                  <p className="text-white text-2xl font-bold">{analytics.totalWatched}</p>
                </div>
                <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-amber-400" />
                    <span className="text-gray-400 text-sm">Watching</span>
                  </div>
                  <p className="text-white text-2xl font-bold">{analytics.currentlyWatching}</p>
                </div>
                <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Award className="w-4 h-4 text-blue-400" />
                    <span className="text-gray-400 text-sm">Total</span>
                  </div>
                  <p className="text-white text-2xl font-bold">{analytics.totalMoviesInteracted}</p>
                </div>
              </div>
            </div>

            {/* Additional Info Section */}
            <div className="mt-8 pt-6 border-t border-white/10">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {analytics.favoriteGenres.length > 0 && (
                  <div>
                    <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                      Favorite Genres
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {analytics.favoriteGenres.map((genre, index) => (
                        <span key={index} className="bg-gray-700/50 text-gray-300 px-3 py-1 rounded-lg text-sm border border-gray-600/50">
                          {genre}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {analytics.currentlyWatchingMovies.length > 0 && (
                  <div>
                    <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 bg-amber-400 rounded-full"></span>
                      Currently Watching
                    </h3>
                    <div className="space-y-2">
                      {analytics.currentlyWatchingMovies.slice(0, 3).map((item, index) => (
                        <div key={item.movie.movie_id} className="text-sm">
                          <Link 
                            to={`/movie/${item.movie.movie_id}`} 
                            className="text-amber-300 hover:text-amber-200 transition-colors duration-200 block truncate"
                          >
                            {item.movie.title}
                          </Link>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {analytics.highestRated.length > 0 && (
                  <div>
                    <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                      Highest Rated
                    </h3>
                    <div className="space-y-2">
                      {analytics.highestRated.slice(0, 3).map((item, index) => (
                        <div key={item.movie.movie_id} className="text-sm">
                          <Link 
                            to={`/movie/${item.movie.movie_id}`} 
                            className="text-purple-300 hover:text-purple-200 transition-colors duration-200 block truncate"
                          >
                            {item.movie.title}
                          </Link>
                          <span className="text-gray-400"> - {item.user_action.rating}/10</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Movie Lists - Full Width Below */}
        <div>
          <HorizontalMovieList
            title={isOwnProfile ? "Your Favorite Movies" : `${profileUser.username}'s Favorite Movies`}
            movies={favorites}
            emptyMessage={isOwnProfile ? "You haven't favorited any movies yet." : "No favorite movies yet."}
          />
          
          <HorizontalMovieList
            title={isOwnProfile ? "Your Watched Movies" : `${profileUser.username}'s Watched Movies`}
            movies={watched}
            emptyMessage={isOwnProfile ? "You haven't watched any movies yet." : "No watched movies yet."}
          />
        </div>
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
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
};

export default UserPage;
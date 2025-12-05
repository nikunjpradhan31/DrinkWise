import React, { useState, useEffect } from "react";
import { Container, Row, Col, Card, Button, Spinner, Alert, Modal, Form, Dropdown, ListGroup, Image } from "react-bootstrap";
import { useMovieContext } from "../context/MovieContext";
import { useAuthContext } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import EditModal from "../components/EditModal";
import { List, Plus, Edit, Trash2, LogOut, Users, Calendar, Eye, EyeOff, Star, Loader2, AlertCircle, CheckCircle, Search } from "lucide-react";

const WatchlistPage = () => {
  const { user } = useAuthContext();
  const navigate = useNavigate();

  const {
    watchlists,
    isWatchListGettingLoading,
    getWatchListError,
    fetchUserWatchlists,
    updateWatchlist,
    deleteWatchlist,
    getGuestWatchlists,
    guest_watchlists,
    removeGuestFromWatchlist,
    createWatchlist,
    getMoviesInWatchlist,
    deleteMovieFromWatchlist,
    getWatchlistRecommendations,
    addMovieToWatchlist
  } = useMovieContext();

  // State management
  const [isGuestLoading, setIsGuestLoading] = useState(true);
  const [guestError, setGuestError] = useState(null);
  const [selectedWatchlist, setSelectedWatchlist] = useState(null);
  const [selectedWatchlistData, setSelectedWatchlistData] = useState(null);
  const [activeView, setActiveView] = useState("watchlist"); // "watchlist", "create", "find"
  // Modal states
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [recommended_movies, setRecommendedMovies] = useState([])
  const [editFormData, setEditFormData] = useState({
    watchlist_id: undefined,
    watchlist_title: "",
  });

  // Create form states
  const [createFormData, setCreateFormData] = useState({
    watchlist_title: "",
  });
  const [isCreating, setIsCreating] = useState(false);

  // Search states
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  // Watchlist movies states
  const [watchlistMovies, setWatchlistMovies] = useState([]);
  const [isMoviesLoading, setIsMoviesLoading] = useState(false);
  const [moviesError, setMoviesError] = useState(null);

  useEffect(() => {
    fetchGuestLists();
    fetchUserWatchlists();
  }, [user?.user_id]);

  const fetchGuestLists = async () => {
    try {
      if (user?.user_id) await getGuestWatchlists(user?.user_id, user.access_token);
    } catch (error) {
      setGuestError("Failed to fetch guest watchlists.");
    } finally {
      setIsGuestLoading(false);
    }
  };

  const handleWatchlistSelect = async (watchlistId) => {
    setSelectedWatchlist(watchlistId);
    setActiveView("watchlist");
    
    // Find the watchlist data
    const watchlistData = 
      watchlists?.find((w) => w.watchlist_id === watchlistId) ||
      guest_watchlists?.find((w) => w.watchlist_id === watchlistId);
    
    setSelectedWatchlistData(watchlistData);

    // Fetch movies for the selected watchlist
    if (watchlistData) {
      try {
        setIsMoviesLoading(true);
        setMoviesError(null);
        const movies = await getMoviesInWatchlist(watchlistId);
        setWatchlistMovies(movies || []);
        const recommended_movies = await getWatchlistRecommendations(watchlistData.watchlist_id)
        setRecommendedMovies(recommended_movies)
      } catch (error) {
        setMoviesError("Failed to fetch movies in the watchlist. Please try again.");
        setWatchlistMovies([]);
      } finally {
        setIsMoviesLoading(false);
      }
    }
  };

  const getUserRole = (watchlist) => {
    // Check if user is owner
    if (watchlist.owner === user.user_id) {
      return "Owner";
    }
    // Check if user is guest
    if (watchlist.role === "Editor") {
      return "Editor"; 
    }

    return "Viewer";
  };

  const isUserOwner = (watchlist) => {
    return watchlist?.role !== "Viewer"
  };

  const handleEditWatchlist = (watchlist) => {
    setEditFormData({
      watchlist_id: watchlist.watchlist_id,
      watchlist_title: watchlist.watchlist_title,
    });
    setShowEditModal(true);
  };

  const handleDeleteWatchlist = (watchlist) => {
    setEditFormData({ watchlist_id: watchlist.watchlist_id });
    setShowDeleteModal(true);
  };

  const handleLeaveWatchlist = async (watchlistId) => {
    if (!user?.user_id) return;
    try {
      await removeGuestFromWatchlist(watchlistId, user.user_id, user.access_token);
      fetchGuestLists();
      if (selectedWatchlist === watchlistId) {
        setSelectedWatchlist(null);
        setSelectedWatchlistData(null);
      }
    } catch (error) {
      console.error("Error leaving watchlist:", error.message);
    }
  };

  const handleUpdateWatchlist = async () => {
    try {
      await updateWatchlist({
        watchlist_id: editFormData.watchlist_id,
        watchlist_title: editFormData.watchlist_title,
        owner: 0,
        access_token: user.access_token,
      });
      await fetchUserWatchlists();
      setShowEditModal(false);
      setEditFormData({ watchlist_id: undefined, watchlist_title: "" });
    } catch (error) {
      console.error("Error updating watchlist:", error);
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteWatchlist(editFormData.watchlist_id);
      await fetchUserWatchlists();
      setShowDeleteModal(false);
      if (selectedWatchlist === editFormData.watchlist_id) {
        setSelectedWatchlist(null);
        setSelectedWatchlistData(null);
      }
    } catch (error) {
      console.error("Error deleting watchlist:", error);
    }
  };

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    if (!createFormData.watchlist_title.trim()) return;

    try {
      setIsCreating(true);
      await createWatchlist({
        watchlist_title: createFormData.watchlist_title,
        user_id: user.user_id,
        access_token: user.access_token,
      });
      await fetchUserWatchlists();
      setCreateFormData({ watchlist_title: ""});
      setActiveView("watchlist");
    } catch (error) {
      console.error("Error creating watchlist:", error);
    } finally {
      setIsCreating(false);
    }
  };

  const allWatchlists = [
    ...(watchlists || []).map(w => ({ ...w, isOwner: true })),
    ...(guest_watchlists || []).map(w => ({ ...w, isOwner: false }))
  ];

const [openDropdown, setOpenDropdown] = useState(null);

const handleDropdownToggle = (watchlistId) => {
  setOpenDropdown(openDropdown === watchlistId ? null : watchlistId);
};

useEffect(() => {
  const handleClickOutside = () => {
    setOpenDropdown(null);
  };

  if (openDropdown) {
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }
}, [openDropdown]);

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
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Left Sidebar - Watchlists */}
        <div className="lg:col-span-1">
          <div className="sticky top-24">
            <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
              {/* Header */}
              <div className="p-6 border-b border-white/10">
                <div className="flex items-center gap-3 mb-4">
                  <List className="w-6 h-6 text-purple-400" />
                  <h4 className="text-xl font-bold text-white">Watchlists</h4>
                </div>
                
                <button
                  onClick={() => setActiveView("create")}
                  className={`w-full flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-300 hover:scale-105 ${
                    activeView === "create" 
                      ? "bg-purple-600/30 border border-purple-500/50 text-purple-300" 
                      : "bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white"
                  }`}
                >
                  <Plus className="w-4 h-4" />
                  Create New
                </button>
              </div>

              {/* Watchlists List */}
              <div className="max-h-[60vh] overflow-y-auto">
                {(isWatchListGettingLoading || isGuestLoading) ? (
                  <div className="p-6 flex items-center justify-center">
                    <div className="flex items-center gap-3 text-purple-400">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Loading watchlists...</span>
                    </div>
                  </div>
                ) : (getWatchListError || guestError) ? (
                  <div className="p-4 m-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <div className="flex items-center gap-3 text-red-400">
                      <AlertCircle className="w-5 h-5" />
                      <span className="text-sm">{getWatchListError || guestError}</span>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2 p-4">
                    {allWatchlists.length === 0 ? (
                      <div className="text-center py-8">
                        <List className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-500 text-sm">No watchlists yet</p>
                      </div>
                    ) : (
                      allWatchlists.map((watchlist) => (
                        <div
                          key={watchlist.watchlist_id}
                          onClick={() => handleWatchlistSelect(watchlist.watchlist_id)}
                          className={`group relative p-4 rounded-lg border cursor-pointer transition-all duration-300 hover:scale-105 ${
                            selectedWatchlist === watchlist.watchlist_id
                              ? "bg-purple-600/20 border-purple-500/50 text-purple-300"
                              : "bg-white/5 hover:bg-white/10 border-white/10 text-gray-300 hover:text-white"
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-grow-1 min-w-0">
                              <div className="font-semibold text-sm mb-1 truncate">
                                {watchlist.watchlist_title}
                              </div>
                              <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
                                <Users className="w-3 h-3" />
                                <span>{watchlist.number_of_movies || 0} movies</span>
                              </div>
                              <div className="flex items-center gap-1 text-xs">
                                
                                <span className="text-gray-500 ml-2">{getUserRole(watchlist)}</span>
                              </div>
                            </div>
                            
                            {/* Dropdown Menu */}
                            <div className="relative" onClick={(e) => e.stopPropagation()}>
  <button 
    className="p-1 hover:bg-white/10 rounded transition-colors opacity-30 group-hover:opacity-100"
    onClick={(e) => {
      e.stopPropagation();
      handleDropdownToggle(watchlist.watchlist_id);
    }}
  >
    <div className="w-1 h-1 bg-current rounded-full mb-1"></div>
    <div className="w-1 h-1 bg-current rounded-full mb-1"></div>
    <div className="w-1 h-1 bg-current rounded-full"></div>
  </button>
  
  {/* Dropdown menu */}
  <div className={`absolute right-0 top-8 bg-black/90 backdrop-blur-xl border border-white/20 rounded-lg shadow-2xl min-w-32 z-50 transition-all duration-200 ${
    openDropdown === watchlist.watchlist_id 
      ? 'opacity-100 scale-100 pointer-events-auto' 
      : 'opacity-0 scale-95 pointer-events-none'
  }`}>
    {watchlist.isOwner ? (
      <>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            handleEditWatchlist(watchlist);
            setOpenDropdown(null);
          }}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-colors first:rounded-t-lg"
        >
          <Edit className="w-3 h-3" />
          Edit
        </button>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            handleDeleteWatchlist(watchlist);
            setOpenDropdown(null);
          }}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors last:rounded-b-lg"
        >
          <Trash2 className="w-3 h-3" />
          Delete
        </button>
      </>
    ) : (
      <button 
        onClick={(e) => {
          e.stopPropagation();
          handleLeaveWatchlist(watchlist.watchlist_id);
          setOpenDropdown(null);
        }}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors rounded-lg"
      >
        <LogOut className="w-3 h-3" />
        Leave
      </button>
    )}
  </div>
</div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Content Area */}
        <div className="lg:col-span-3">
          
          {/* Create New Watchlist */}
          {activeView === "create" && (
            <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
              <div className="p-6 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <Plus className="w-6 h-6 text-purple-400" />
                  <h5 className="text-xl font-bold text-white">Create New Watchlist</h5>
                </div>
              </div>
              
              <div className="p-6">
                <form onSubmit={handleCreateWatchlist} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-purple-300 mb-2">
                      Watchlist Title
                    </label>
                    <input
                      type="text"
                      value={createFormData.watchlist_title}
                      onChange={(e) =>
                        setCreateFormData(prev => ({
                          ...prev,
                          watchlist_title: e.target.value,
                        }))
                      }
                      placeholder="Enter watchlist name"
                      required
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all duration-300"
                    />
                  </div>
                  
                  
                  
                  <button
                    type="submit"
                    disabled={isCreating || !createFormData.watchlist_title.trim()}
                    className="flex items-center gap-2 px-6 py-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 rounded-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4" />
                        Create Watchlist
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Watchlist Details */}
          {activeView === "watchlist" && selectedWatchlistData && (
            <div className="space-y-6">
              {/* Watchlist Header */}
              <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-white/10">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <h5 className="text-2xl font-bold text-white">{selectedWatchlistData.watchlist_title}</h5>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        {/* {selectedWatchlistData.is_private ? (
                          <>
                            <EyeOff className="w-4 h-4 text-yellow-400" />
                            <span className="text-yellow-400">Private</span>
                          </>
                        ) : (
                          <>
                            <Eye className="w-4 h-4 text-green-400" />
                            <span className="text-green-400">Public</span>
                          </>
                        )} */}
                      </div>
                      <div className="flex items-center gap-2 text-gray-400">
                        <Users className="w-4 h-4" />
                        <span>{selectedWatchlistData.number_of_movies || 0} movies</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-gray-300">
                    {/* <div className="flex items-center gap-3">
                      {selectedWatchlistData.is_private ? (
                        <EyeOff className="w-5 h-5 text-yellow-400" />
                      ) : (
                        <Eye className="w-5 h-5 text-green-400" />
                      )}
                      <div>
                        <span className="text-purple-300 font-medium">Privacy:</span>
                        <p className={`${selectedWatchlistData.is_private ? "text-yellow-400" : "text-green-400"}`}>
                          {selectedWatchlistData.is_private ? "Private" : "Public"}
                        </p>
                      </div>
                    </div> */}
                    
                    <div className="flex items-center gap-3">
                      <Calendar className="w-5 h-5 text-purple-400" />
                      <div>
                        <span className="text-purple-300 font-medium">Created:</span>
                        <p className="text-white">
                          {selectedWatchlistData.created_at 
                            ? new Date(selectedWatchlistData.created_at).toLocaleDateString()
                            : "N/A"
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Users className="w-5 h-5 text-purple-400" />
                      <div>
                        <span className="text-purple-300 font-medium">Role:</span>
                        <p className="text-white">{getUserRole(selectedWatchlistData)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Movies Section */}
              {isMoviesLoading ? (
                <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
                  <div className="flex items-center justify-center gap-4 text-purple-400">
                    <Loader2 className="w-8 h-8 animate-spin" />
                    <span className="text-lg">Loading movies...</span>
                  </div>
                </div>
              ) : moviesError ? (
                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 shadow-2xl">
                  <div className="flex items-center gap-3 text-red-400">
                    <AlertCircle className="w-6 h-6" />
                    <span>{moviesError}</span>
                  </div>
                </div>
              ) : watchlistMovies.length > 0 ? (
                <div className="space-y-6">
                  {/* Movies in Watchlist */}
                  <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                    <div className="p-6 border-b border-white/10">
                      <h6 className="text-lg font-semibold text-white">Movies in Watchlist</h6>
                    </div>
                    
                    <div className="p-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {watchlistMovies.map((movie) => (
                          <div key={movie.movie_id} className="group">
                            <div className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl overflow-hidden transition-all duration-300 hover:scale-105 h-full">
                              <div className="flex h-full">
                                <div className="flex-shrink-0">
                                  <img
                                    src={movie.image_url}
                                    alt={movie.title}
                                    className="w-20 h-32 object-cover"
                                  />
                                </div>
                                <div className="flex flex-col justify-between p-4 flex-grow">
                                  <div>
                                    <h6 className="font-semibold text-white text-sm mb-2 line-clamp-2">
                                      {movie.title}
                                    </h6>
                                    <div className="flex items-center gap-2 mb-3">
                                      <Star className="w-4 h-4 text-yellow-400" />
                                      <span className="text-yellow-400 text-sm font-medium">
                                        {movie.rating}/10
                                      </span>
                                    </div>
                                  </div>
                                  
                                  <div className="flex gap-2">
                                    <button
                                      onClick={() => navigate(`/movie/${movie.movie_id}`)}
                                      className="flex-1 px-3 py-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 rounded-lg text-xs transition-all duration-300 hover:scale-105"
                                    >
                                      View
                                    </button>
                                    {isUserOwner(selectedWatchlistData) && (
                                      <button
                                        onClick={(e) => {
                                          e.preventDefault();
                                          e.stopPropagation();
                                          deleteMovieFromWatchlist(selectedWatchlistData.watchlist_id, movie.movie_id);
                                          setWatchlistMovies((prevMovies) =>
                                            prevMovies.filter((m) => m.movie_id !== movie.movie_id)
                                          );
                                        }}
                                        className="px-3 py-2 bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 text-red-300 rounded-lg text-xs transition-all duration-300 hover:scale-105"
                                      >
                                        <Trash2 className="w-3 h-3" />
                                      </button>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Similar Items */}
                  {recommended_movies.length > 0 && (
                    <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                      <div className="p-6 border-b border-white/10">
                        <h6 className="text-lg font-semibold text-white">Similar Items</h6>
                      </div>
                      
                      <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                          {recommended_movies.map((movie) => (
                            <div key={movie.movie_id} className="group">
                              <div className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl overflow-hidden transition-all duration-300 hover:scale-105 h-full">
                                <div className="flex h-full">
                                  <div className="flex-shrink-0">
                                    <img
                                      src={movie.image_url}
                                      alt={movie.title}
                                      className="w-20 h-32 object-cover"
                                    />
                                  </div>
                                  <div className="flex flex-col justify-between p-4 flex-grow">
                                    <div>
                                      <h6 className="font-semibold text-white text-sm mb-2 line-clamp-2">
                                        {movie.title}
                                      </h6>
                                      <div className="flex items-center gap-2 mb-3">
                                        <Star className="w-4 h-4 text-yellow-400" />
                                        <span className="text-yellow-400 text-sm font-medium">
                                          {movie.rating}/10
                                        </span>
                                      </div>
                                    </div>
                                    
                                    <div className="flex gap-2">
                                      <button
                                        onClick={() => navigate(`/movie/${movie.movie_id}`)}
                                        className="flex-1 px-3 py-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 rounded-lg text-xs transition-all duration-300 hover:scale-105"
                                      >
                                        View
                                      </button>
                                      {isUserOwner(selectedWatchlistData) && (
                                        <button
                                          onClick={(e) => {
                                            e.preventDefault();
                                            e.stopPropagation();
                                            addMovieToWatchlist(selectedWatchlistData.watchlist_id, movie.movie_id);
                                            setWatchlistMovies([...watchlistMovies, movie]);
                                            setRecommendedMovies((prevMovies) =>
                                              prevMovies.filter((m) => m.movie_id !== movie.movie_id)
                                            );
                                          }}
                                          className="px-3 py-2 bg-green-600/20 hover:bg-green-600/30 border border-green-500/30 text-green-300 rounded-lg text-xs transition-all duration-300 hover:scale-105"
                                        >
                                          <Plus className="w-3 h-3" />
                                        </button>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
                  <div className="text-center py-8">
                    <List className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-6 inline-block">
                      <h6 className="text-white font-semibold mb-2">No movies in this watchlist yet</h6>
                      <p className="text-gray-400 mb-4">Start adding movies to build your collection!</p>
                      <button 
                        onClick={() => navigate("/")}
                        className="flex items-center gap-2 px-6 py-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-purple-300 rounded-lg transition-all duration-300 hover:scale-105 mx-auto"
                      >
                        <Search className="w-4 h-4" />
                        Find Movies
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* No Watchlist Selected */}
          {activeView === "watchlist" && !selectedWatchlistData && (
            <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
              <div className="text-center py-12">
                <List className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h5 className="text-xl font-semibold text-white mb-2">Select a watchlist to view its contents</h5>
                <p className="text-gray-400">Choose a watchlist from the sidebar to see movies and details</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      <EditModal 
        showEditModal={showEditModal} 
        setShowEditModal={setShowEditModal} 
        editFormData={editFormData} 
        setEditFormData={setEditFormData} 
        handleUpdateWatchlist={handleUpdateWatchlist} 
        user={user} 
      />

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-black/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl max-w-md w-full">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-red-400" />
                <h3 className="text-xl font-bold text-white">Confirm Delete</h3>
              </div>
            </div>
            
            <div className="p-6">
              <p className="text-gray-300 mb-6">
                Are you sure you want to delete this watchlist? This action cannot be undone.
              </p>
              
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 rounded-lg transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 text-red-300 rounded-lg transition-all duration-300 hover:scale-105"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  </div>
);
};

export default WatchlistPage;
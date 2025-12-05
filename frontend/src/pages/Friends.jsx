import React, { useState, useEffect } from "react";
import { useAuthContext } from "../context/AuthContext";
import { useMovieContext } from "../context/MovieContext";
import { useNavigate } from "react-router-dom";
import { Search, Loader2, AlertCircle, X, UserPlus, Check, XCircle, Users, Heart, Eye, Edit3 } from 'lucide-react';

import { axiosInstance } from "../utils/axiosHelper";
import { Link } from "react-router-dom";
const FriendsPage = () => {
  const {
    user,
    friends,
    fetchFriends,
    friendError,
    isFriendLoading,
    sendFriendRequest,
    friendRequestError,
    isFriendRequestLoading,
    removeFriend,
    removeFriendError,
    isRemoveFriendLoading,
    setFriends,
  } = useAuthContext();

  const {
    watchlists,
    fetchUserWatchlists,
    fetchRecommendationsForUser,
  } = useMovieContext();

  const navigate = useNavigate();

  // Search states
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchError, setSearchError] = useState(null);
  const [isSearchLoading, setIsSearchLoading] = useState(false);

  // Modal and confirmation states
  const [showWatchlistModal, setShowWatchlistModal] = useState(false);
  const [showRemoveConfirm, setShowRemoveConfirm] = useState(false);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [selectedWatchlist, setSelectedWatchlist] = useState("");
  const [selectedRole, setSelectedRole] = useState("VIEWER");

  // Recommendations states
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationError, setRecommendationError] = useState(null);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(true);

  // Feedback states
  const [feedbackMessage, setFeedbackMessage] = useState(null);
  const [feedbackVariant, setFeedbackVariant] = useState(undefined);

  // Friend requests states
  const [friendRequests, setFriendRequests] = useState([]);
  const [isLoadingRequests, setIsLoadingRequests] = useState(false);
  const [requestsError, setRequestsError] = useState(null);

  useEffect(() => {
    if (user) {
      fetchUserWatchlists();
      fetchRecommendations();
      handleGetFriendRequests(user.user_id, user.access_token);
    }
  }, [user, fetchUserWatchlists]);

  useEffect(() => {
    if (user) fetchFriends();
  }, [user, fetchFriends]);

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsSearchLoading(true);
    setSearchError(null);

    if (searchTerm.trim() === "") {
      setIsSearchLoading(false);
      setSearchResults([]);
      return;
    }

    try {
      const response = await axiosInstance.get(
        `/users/search/${searchTerm}/${user?.username}`
      );
      setSearchResults(response.data);
    } catch (error) {
      setSearchError("Error fetching search results.");
    } finally {
      setIsSearchLoading(false);
    }
  };

  const handleAddFriend = async (friend) => {
    if (!user) return;

    try {
      const response = await sendFriendRequest(friend?.user_id);

      if (response?.status === 201) {
        setSearchTerm("");
        setSearchResults([]);
        setFeedbackMessage(`Sent friend request to ${friend.username}.`);
        setFeedbackVariant("success");
      }
    } catch (error) {
      console.error("Error adding friend:", error);
      setFeedbackMessage(`${friend.username} is already your friend.`);
      setFeedbackVariant("danger");
      setSearchTerm("");
      setSearchResults([]);
    }
  };

  const handleRemoveFriendConfirm = (friend) => {
    setSelectedFriend(friend);
    setShowRemoveConfirm(true);
  };

  const handleRemoveFriend = async () => {
    if (!user || !selectedFriend) return;

    try {
      await removeFriend(selectedFriend?.user_id);
      setFeedbackMessage(`${selectedFriend.username} has been removed.`);
      setFeedbackVariant("success");
      setShowRemoveConfirm(false);
      setSelectedFriend(null);
    } catch (error) {
      setFeedbackMessage("Failed to remove friend. Please try again.");
      setFeedbackVariant("danger");
    }
  };

  const handleShowWatchlistModal = (friend) => {
    setSelectedFriend(friend);
    setSelectedWatchlist("");
    setSelectedRole("VIEWER");
    setShowWatchlistModal(true);
  };

  const handleAddGuestToWatchlist = async () => {
    if (!selectedWatchlist || !selectedFriend) return;

    try {
      await axiosInstance.post("/watchlist/add_guest", {
        watchlist_id: selectedWatchlist,
        user_id: selectedFriend.user_id,
        role: selectedRole,
        access_token: user.access_token,
      });
      setFeedbackMessage(
        `${selectedFriend.username} has been added to the watchlist as ${selectedRole}.`
      );
      setFeedbackVariant("success");
      setShowWatchlistModal(false);
    } catch (error) {
      console.error("Error adding friend as a guest:", error.message);
      setFeedbackMessage("Friend is already in watchlist.");
      setFeedbackVariant("danger");
    }
  };

  const fetchRecommendations = async () => {
    try {
      if (user?.user_id) {
        setIsLoadingRecommendations(true);
        const data = await fetchRecommendationsForUser(
          user.user_id,
          user.access_token
        );
        setRecommendations(data);
      }
    } catch (error) {
      setRecommendationError("Failed to load recommendations.");
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const navigateToMovie = (movieId) => {
    navigate(`/movie/${movieId}`);
  };

  const handleFriendProfileClick = (friend) => {
    // Navigate to friend's profile - implement route later
    console.log(`Navigate to ${friend.username}'s profile`);
  };

const handleDeleteRecommendation = async (recommendation,movie_id) => {
  if (!user) return;

  try {
    const response = await axiosInstance.post("/users/recommendation/delete", {
       
        requesting_user_id: user.user_id,
        other_user_id: recommendation.recommender,
        movie_id: movie_id,
        is_recommender: false,
        access_token: user.access_token
  
    });

    if (response.status === 204) {
      setFeedbackMessage("Recommendation removed successfully.");
      setFeedbackVariant("success");
      setRecommendations((prev) =>
  prev
    .map((rec) => {
      if (rec.recommender === recommendation.recommender) {
        return {
          ...rec,
          movies: rec.movies.filter((movie) => movie.movie_id !== movie_id),
        };
      }
      return rec;
    })
    .filter((rec) => rec.movies.length > 0) // Remove empty groups
);



    }
  } catch (error) {
    console.error("Error deleting recommendation:", error);
    setFeedbackMessage("Failed to delete recommendation.");
    setFeedbackVariant("danger");
  }
};

  const handleGetFriendRequests = async (userId, accessToken) => {
    setIsLoadingRequests(true);
    setRequestsError(null);
    try {
      const response = await axiosInstance.get(`/users/friends/get_all_requests/${userId}/${accessToken}`);
      if (response.status === 200) {
        setFriendRequests(response.data.friends || []);
      }
    } catch (error) {
      if (error.response?.status === 204) {
        setFriendRequests([]);
      } else {
        console.error("Error fetching friend requests:", error);
        setRequestsError("Failed to load friend requests.");
      }
    } finally {
      setIsLoadingRequests(false);
    }
  };

  const handleAcceptFriendRequest = async (requesterId) => {
    try {
      // Add your accept friend request API call here
      const response = await axiosInstance.post('/users/friends/accept_request', {
        user_one: requesterId,
        user_two: user.user_id,
        access_token: user.access_token
      });
      
      if (!response.error) {
        // Remove from requests and refresh friends list
        setFriendRequests(prev => prev.filter(req => req.user_id !== requesterId));
        fetchFriends();
        setFeedbackMessage("Friend request accepted!");
        setFeedbackVariant("success");
      }
    } catch (error) {
      console.error("Error accepting friend request:", error);
      setFeedbackMessage("Failed to accept friend request.");
      setFeedbackVariant("danger");
    }
  };

  const handleDeclineFriendRequest = async (requesterId) => {

    try {
      // Add your decline friend request API call here
      await removeFriend(requesterId);

        // Remove from requests
        setFriendRequests(prev => prev.filter(req => req.user_id !== requesterId));
        setFeedbackMessage("Friend request declined.");
        setFeedbackVariant("info");
    } catch (error) {
      console.error("Error declining friend request:", error);
      setFeedbackMessage("Failed to decline friend request.");
      setFeedbackVariant("danger");
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
        
        {/* Search Section */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl mb-8">
          <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-xl p-4 mb-6">
            <h4 className="text-white text-xl font-semibold mb-0 flex items-center gap-3">
              <Search className="w-6 h-6 text-purple-400" />
              Search for Users
            </h4>
          </div>
          
          <form onSubmit={handleSearch} className="mb-4">
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="Enter a username to search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all duration-200"
              />
              <button
                type="submit"
                disabled={isSearchLoading}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 text-white px-6 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 disabled:cursor-not-allowed"
              >
                {isSearchLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Search className="w-5 h-5" />
                )}
                Search
              </button>
            </div>
          </form>

          {searchError && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mt-4">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>{searchError}</span>
              </div>
            </div>
          )}

          {searchResults.length > 0 && (
            <div className="mt-6">
              <h6 className="text-gray-300 text-lg font-medium mb-4">Search Results:</h6>
              <div className="space-y-3">
                {searchResults.map((result) => (
                  <div
                    key={result.username}
                    className="bg-white/5 border border-white/10 rounded-xl p-4 flex justify-between items-center hover:bg-white/10 transition-all duration-200"
                  >
                    <span className="text-white font-medium">{result.username}</span>
                    <button
                      onClick={() => handleAddFriend(result)}
                      disabled={isFriendRequestLoading}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 disabled:cursor-not-allowed"
                    >
                      <UserPlus className="w-4 h-4" />
                      Add Friend
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Feedback Alert */}
        {feedbackMessage && (
          <div className={`${feedbackVariant === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'} border rounded-xl p-4 mb-8 flex items-center justify-between`}>
            <div className="flex items-center gap-3">
              {feedbackVariant === 'success' ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              <span>{feedbackMessage}</span>
            </div>
            <button
              onClick={() => setFeedbackMessage(null)}
              className="text-gray-400 hover:text-white transition-colors duration-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Friend Requests Section */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl mb-8">
          <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 border border-yellow-500/30 rounded-xl p-4 mb-6 flex justify-between items-center">
            <h4 className="text-white text-xl font-semibold mb-0 flex items-center gap-3">
              <Heart className="w-6 h-6 text-yellow-400" />
              Friend Requests
            </h4>
            <span className="bg-yellow-500/20 text-yellow-300 px-3 py-1 rounded-full text-sm font-medium border border-yellow-500/30">
              {friendRequests?.length || 0} pending
            </span>
          </div>
          
          {isLoadingRequests ? (
            <div className="text-center py-8">
              <div className="bg-white/5 rounded-xl p-6 inline-block">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400 mx-auto mb-3" />
                <p className="text-gray-300">Loading friend requests...</p>
              </div>
            </div>
          ) : requestsError ? (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>{requestsError}</span>
              </div>
            </div>
          ) : friendRequests && friendRequests.length > 0 ? (
            <div className="space-y-3">
              {friendRequests.map((request) => (
                <div
                  key={request.user_id}
                  className="bg-white/5 border border-white/10 rounded-xl p-4 flex justify-between items-center hover:bg-white/10 transition-all duration-200"
                >
                  <div>
                    <h6 className="text-white text-lg font-medium mb-1">{request.username}</h6>
                    <p className="text-gray-400 text-sm">Wants to be your friend</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAcceptFriendRequest(request.user_id)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
                    >
                      <Check className="w-4 h-4" />
                      Accept
                    </button>
                    <button
                      onClick={() => handleDeclineFriendRequest(request.user_id)}
                      className="bg-transparent border border-red-500/50 hover:bg-red-500/10 text-red-400 px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
                    >
                      <XCircle className="w-4 h-4" />
                      Decline
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="bg-white/5 rounded-xl p-6 inline-block">
                <p className="text-gray-400">No pending friend requests.</p>
              </div>
            </div>
          )}
        </div>

        {/* Friends Section */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl mb-8">
          <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl p-4 mb-6 flex justify-between items-center">
            <h4 className="text-white text-xl font-semibold mb-0 flex items-center gap-3">
              <Users className="w-6 h-6 text-green-400" />
              My Friends
            </h4>
            <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-sm font-medium border border-green-500/30">
              {friends?.length || 0} friends
            </span>
          </div>
          
          {isFriendLoading ? (
            <div className="text-center py-8">
              <div className="bg-white/5 rounded-xl p-6 inline-block">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400 mx-auto mb-3" />
                <p className="text-gray-300">Loading friends...</p>
              </div>
            </div>
          ) : friendError ? (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>{friendError}</span>
              </div>
            </div>
          ) : friends && friends.length > 0 ? (
            <div className="space-y-3">
              {friends.map((friend) => (
                <div
                  key={friend.username}
                  className="bg-white/5 border border-white/10 rounded-xl p-4 flex justify-between items-center hover:bg-white/10 transition-all duration-200"
                >
                  <div>
                    <Link 
                      to={`/profile/${friend.user_id}`}
                      className="text-purple-400 hover:text-purple-300 text-lg font-medium transition-colors duration-200 cursor-pointer"
                      onClick={() => handleFriendProfileClick(friend)}
                    >
                      {friend.username}
                    </Link>
                    <p className="text-gray-400 text-sm">Click to view profile</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleShowWatchlistModal(friend)}
                      className="bg-transparent border border-purple-500/50 hover:bg-purple-500/10 text-purple-400 px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
                    >
                      <Eye className="w-4 h-4" />
                      Add to Watchlist
                    </button>
                    <button
                      onClick={() => handleRemoveFriendConfirm(friend)}
                      disabled={isRemoveFriendLoading}
                      className="bg-transparent border border-red-500/50 hover:bg-red-500/10 text-red-400 px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <X className="w-4 h-4" />
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="bg-white/5 rounded-xl p-6 inline-block">
                <p className="text-gray-400">No friends added yet. Search for users to add them as friends!</p>
              </div>
            </div>
          )}
        </div>

        {/* Recommendations Section */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
          <div className="bg-gradient-to-r from-blue-600/20 to-cyan-600/20 border border-blue-500/30 rounded-xl p-4 mb-6">
            <h4 className="text-white text-xl font-semibold mb-0 flex items-center gap-3">
              <Heart className="w-6 h-6 text-blue-400" />
              Movie Recommendations
            </h4>
          </div>
          
          {isLoadingRecommendations ? (
            <div className="text-center py-8">
              <div className="bg-white/5 rounded-xl p-6 inline-block">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400 mx-auto mb-3" />
                <p className="text-gray-300">Loading recommendations...</p>
              </div>
            </div>
          ) : recommendationError ? (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>{recommendationError}</span>
              </div>
            </div>
          ) : recommendations.length > 0 && friends ? (
            <div className="space-y-8">
              {recommendations.map((rec) => (
                <div key={rec.recommender}>
                  <h5 className="text-blue-400 text-lg font-semibold mb-4">
                    Recommended by{" "}
                    {friends.find((friend) => friend.user_id === rec.recommender)
                      ?.username || "Unknown User"}
                  </h5>
                  <div className="flex overflow-x-auto gap-4 pb-4 scrollbar-hide">
                    {rec.movies.map((movie) => (
                      <div
                        key={movie.movie_id}
                        className="relative group min-w-[200px] bg-white/5 border border-white/10 rounded-xl overflow-hidden hover:bg-white/10 transition-all duration-200 cursor-pointer"
                        onClick={() => navigateToMovie(movie.movie_id)}
                      >
                        {/* Remove button */}
                        <button
                          className="absolute top-2 right-2 z-10 bg-red-500/80 hover:bg-red-500 text-white rounded-full p-1 transition-all duration-200 group-hover:opacity-100"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteRecommendation(rec, movie.movie_id);
                          }}
                        >
                          <X className="w-4 h-4" />
                        </button>
                        
                        <img
                          src={movie.image_url || "https://via.placeholder.com/200"}
                          alt={movie.title}
                          className="w-full h-[300px] object-cover"
                        />
                        <div className="p-4">
                          <h6 className="text-white text-center font-medium">{movie.title}</h6>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="bg-white/5 rounded-xl p-6 inline-block">
                <p className="text-gray-400">No recommendations yet. Your friends haven't recommended any movies!</p>
              </div>
            </div>
          )}
        </div>

        {/* Add to Watchlist Modal */}
        {showWatchlistModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-black/80 backdrop-blur-xl border border-white/20 rounded-2xl p-6 w-full max-w-md shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-white text-xl font-semibold">
                  Add {selectedFriend?.username} to Watchlist
                </h3>
                <button
                  onClick={() => setShowWatchlistModal(false)}
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-gray-300 text-sm font-medium mb-2 block">Select Watchlist</label>
                  <select
                    value={selectedWatchlist}
                    onChange={(e) => setSelectedWatchlist(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all duration-200"
                  >
                    <option value="">Choose a watchlist...</option>
                    {watchlists?.map((watchlist) => (
                      <option key={watchlist.watchlist_id} value={watchlist.watchlist_id} className="bg-gray-900">
                        {watchlist.watchlist_title}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="text-gray-300 text-sm font-medium mb-2 block">Role</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="role"
                        checked={selectedRole === "VIEWER"}
                        onChange={() => setSelectedRole("VIEWER")}
                        className="w-4 h-4 text-purple-500 bg-transparent border-gray-600 focus:ring-purple-500/50 focus:ring-2"
                      />
                      <span className="text-white flex items-center gap-2">
                        <Eye className="w-4 h-4" />
                        Viewer
                      </span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="role"
                        checked={selectedRole === "EDITOR"}
                        onChange={() => setSelectedRole("EDITOR")}
                        className="w-4 h-4 text-purple-500 bg-transparent border-gray-600 focus:ring-purple-500/50 focus:ring-2"
                      />
                      <span className="text-white flex items-center gap-2">
                        <Edit3 className="w-4 h-4" />
                        Editor
                      </span>
                    </label>
                  </div>
                  <p className="text-gray-400 text-sm mt-2">
                    Viewers can see the watchlist, Editors can modify it.
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowWatchlistModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-xl font-medium transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddGuestToWatchlist}
                  disabled={!selectedWatchlist}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 text-white py-3 rounded-xl font-medium transition-all duration-200 disabled:cursor-not-allowed"
                >
                  Add to Watchlist
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Remove Friend Confirmation Modal */}
        {showRemoveConfirm && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-black/80 backdrop-blur-xl border border-white/20 rounded-2xl p-6 w-full max-w-md shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-white text-xl font-semibold">Confirm Remove Friend</h3>
                <button
                  onClick={() => setShowRemoveConfirm(false)}
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <p className="text-gray-300 mb-6">
                Are you sure you want to remove{" "}
                <strong className="text-white">{selectedFriend?.username}</strong> from your friends list?
                This action cannot be undone.
              </p>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowRemoveConfirm(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-xl font-medium transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleRemoveFriend}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-xl font-medium transition-all duration-200"
                >
                  Remove Friend
                </button>
              </div>
            </div>
          </div>
        )}
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

export default FriendsPage;
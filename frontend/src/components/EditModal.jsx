import React, { useState, useEffect } from 'react';
import { useMovieContext } from '../context/MovieContext';
import { X, Users, Eye, Edit3, Trash2, Loader2, AlertCircle, Film } from 'lucide-react';

const EditModal = ({
  showEditModal,
  setShowEditModal,
  editFormData,
  setEditFormData,
  handleUpdateWatchlist,
  user,
}) => {
  const {
    getAllGuests,
    isFetchingGuests,
    fetchGuestsError,
    updateGuestPermissions,
    isUpdatingGuest,
    updateGuestError,
    removeGuestFromWatchlist
  } = useMovieContext();
  
  // Guest management states
  const [currentGuests, setCurrentGuests] = useState([]);
  const [guestManagementError, setGuestManagementError] = useState(null);

  // Fetch guests when modal opens and watchlist_id is available
  useEffect(() => {
    const fetchGuests = async () => {
      if (showEditModal && editFormData.watchlist_id) {
        setGuestManagementError(null);
        
        try {
          const guestsData = await getAllGuests(editFormData.watchlist_id);
          if (guestsData) {
            setCurrentGuests(guestsData.guests || []);
          } else {
            setCurrentGuests([]);
          }
        } catch (error) {
          setGuestManagementError("Failed to load guests.");
          setCurrentGuests([]);
        }
      }
    };

    fetchGuests();
  }, [showEditModal, editFormData.watchlist_id, getAllGuests]);

  // Clear guests when modal closes
  useEffect(() => {
    if (!showEditModal) {
      setCurrentGuests([]);
      setGuestManagementError(null);
    }
  }, [showEditModal]);

  // Handler functions
  const handleUpdateGuestRole = async (userId, newRole) => {
    setGuestManagementError(null);
    
    try {
      const updateData = {
        watchlist_id: editFormData.watchlist_id,
        user_id: userId,
        access_token: user?.access_token,
        role: newRole.toUpperCase()
      };
      
      const result = await updateGuestPermissions(updateData);
      
      if (result) {
        // Update local state to reflect the change
        setCurrentGuests(prev => 
          prev.map(guest => 
            guest.user_id === userId 
              ? { ...guest, role: newRole }
              : guest
          )
        );
      } else {
        setGuestManagementError("Failed to update guest permissions.");
      }
    } catch (error) {
      setGuestManagementError("An error occurred while updating guest permissions.");
    }
  };

  const handleRemoveGuest = async (userId) => {
    setGuestManagementError(null);
    
    try {
      removeGuestFromWatchlist(editFormData.watchlist_id, userId, user?.access_token)
      setCurrentGuests(prev => prev.filter(guest => guest.user_id !== userId));
    } catch (error) {
      setGuestManagementError("Failed to remove guest.");
    }
  };

  const handleCloseModal = () => {
    setShowEditModal(false);
    setGuestManagementError(null);
  };


  if (!showEditModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleCloseModal}
      ></div>

      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Modal Container */}
      <div className="relative z-10 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Glassmorphism Card */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-700 rounded-xl shadow-lg shadow-purple-500/25">
                <Film className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-xl font-bold text-white">Edit Watchlist</h2>
            </div>
            <button
              onClick={handleCloseModal}
              className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 space-y-6">
            {/* Title Field */}
            <div className="space-y-2">
              <label htmlFor="title" className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <Edit3 className="w-4 h-4" />
                Title
              </label>
              <input
                id="title"
                type="text"
                placeholder="Enter watchlist title"
                value={editFormData.watchlist_title || ''}
                onChange={(e) =>
                  setEditFormData(prev => ({
                    ...prev,
                    watchlist_title: e.target.value,
                  }))
                }
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm hover:bg-white/10"
              />
            </div>

            {/* Guest Management Section */}
            <div className="border-t border-white/10 pt-6">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Manage Guests</h3>
              </div>
              
              {/* Error Messages */}
              {guestManagementError && (
                <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-sm">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <p className="text-red-400 text-sm font-medium">{guestManagementError}</p>
                  </div>
                </div>
              )}

              {fetchGuestsError && (
                <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-sm">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <p className="text-red-400 text-sm font-medium">{fetchGuestsError}</p>
                  </div>
                </div>
              )}

              {updateGuestError && (
                <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-sm">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <p className="text-red-400 text-sm font-medium">{updateGuestError}</p>
                  </div>
                </div>
              )}

              {/* Loading State */}
              {isFetchingGuests ? (
                <div className="text-center py-8">
                  <div className="flex items-center justify-center gap-2 text-gray-400">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Loading guests...</span>
                  </div>
                </div>
              ) : currentGuests.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No guests added to this watchlist</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-60 overflow-y-auto">
                  {currentGuests.map((guest) => (
                    <div key={guest.user_id} className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm hover:bg-white/10 transition-all duration-200">
                      <div className="flex items-center justify-between gap-4">
                        {/* Guest Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30">
                              {guest.role === 'Editor' ? (
                                <Edit3 className="w-3 h-3 mr-1" />
                              ) : (
                                <Eye className="w-3 h-3 mr-1" />
                              )}
                              {guest.role || 'Viewer'}
                            </span>
                          </div>
                          <div className="text-white font-medium text-sm truncate">
                            {guest.username || guest.email}
                          </div>
                          {guest.username && (
                            <div className="text-gray-400 text-xs truncate">{guest.email}</div>
                          )}
                        </div>

                        {/* Role Selector */}
                        <div className="flex-shrink-0">
                          <select
                            value={guest.role || 'Viewer'}
                            onChange={(e) => handleUpdateGuestRole(guest.user_id, e.target.value)}
                            disabled={isUpdatingGuest}
                            className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm hover:bg-white/10 disabled:opacity-50"
                          >
                            <option value="Viewer">Viewer</option>
                            <option value="Editor">Editor</option>
                          </select>
                        </div>

                        {/* Remove Button */}
                        <div className="flex-shrink-0">
                          <button
                            onClick={() => handleRemoveGuest(guest.user_id)}
                            disabled={isUpdatingGuest}
                            className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {isUpdatingGuest ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-white/10">
            <button
              onClick={handleCloseModal}
              className="px-6 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200 font-medium"
            >
              Cancel
            </button>
            <button 
              onClick={handleUpdateWatchlist}
              disabled={isUpdatingGuest}
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg shadow-purple-500/25"
            >
              {isUpdatingGuest ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Saving...</span>
                </div>
              ) : (
                "Save Changes"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditModal;
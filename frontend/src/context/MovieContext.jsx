import React, { createContext, useCallback, useContext, useState, ReactNode } from "react";
import { axiosInstance } from "../utils/axiosHelper";
import { AuthContext } from "./AuthContext";


export const MovieContext = createContext(undefined);


export const MovieContextProvider = ({ children }) => {
  const [movies, setMovies] = useState(null);
  const [searchInfo, setSearchInfo] = useState({ substring: "", page: 1 });
  const [getMovieError, setGetMovieError] = useState(null);
  const [isMovieGettingLoading, setIsMovieGettingLoading] = useState(false);
  const [watchlists, setWatchLists] = useState(null);
  const [getWatchListError, setGetWatchListError] = useState(null);
  const [isWatchListGettingLoading, setIsWatchListGettingLoading] = useState(false);
  const [SingleMovieError, setSingleMovieError] = useState(null);
  const [IsSingleMovieLoading, setIsSingleMovieLoading] = useState(false);
  //const [reviews, setReviews] = useState(null);
  //const [reviewError, setReviewError] = useState(null);
  //const [isReviewLoading, setIsReviewLoading] = useState(false);
  const [guest_watchlists, setguest_watchlists] = useState(null);
  const [singlewatchlists, setsingleWatchLists] = useState(null);
  const [getsingleWatchListError, setGetsingleWatchListError] = useState(null);
  const [issingleWatchListGettingLoading, setIssingleWatchListGettingLoading] = useState(false);
  const [isGenresLoading, setIsGenresLoading] = useState(false);
  const [genresError, setGenresError] = useState(null);
  const [searchmovies, setsearchmovies] = useState([]);
  const [issearchmoviesLoading, setIssearchmoviesLoading] = useState(false);
  const [searchmoviesError, setsearchmoviesError] = useState(null);
  const [totalPages, setsearchtotalpages] = useState(0)
  const auth = useContext(AuthContext);
  if (!auth) {
    throw new Error("AuthContext must be used within an AuthContextProvider");
  }
  const { user } = auth;

  const updateSearchInfo = useCallback((info) => {
    setSearchInfo(info);
  }, []);

  const fetchMovies = useCallback(async () => {
    setIsMovieGettingLoading(true);
    setGetMovieError(null);

    try {
      // const response = await axiosInstance.get(`/movie/search`, {
      //   params: {
      //     substring: searchInfo.substring.trim() || "",
      //     page: searchInfo.page,
      //   },
      // });
      const params = {};
      if (user) {
        params.user_id = user.user_id;
      }
      const response = await axiosInstance.get(`/movie/landing_page_movies`, { params });

      setMovies(response.data);

    } catch (error) {
      setGetMovieError(
        error.response.detail || "Failed to fetch movies. Please try again later."
      );
    } finally {
      setIsMovieGettingLoading(false);
    }
  }, [searchInfo, user?.user_id]);

  const fetchUserWatchlists = useCallback(async () => {
    if (!user?.user_id) {
      console.warn("User is not defined. Fetch aborted.");
      return;
    }

    setIsWatchListGettingLoading(true);
    setGetWatchListError(null);

    try {
      const response = await axiosInstance.get(`/watchlist/get_all/${user.user_id}/${user.access_token}`);
      setWatchLists(response.data.watchlists);
    } catch (error) {
      setGetWatchListError(
        error.response?.data?.detail || "Failed to fetch watchlists. Please try again later."
      );
    } finally {
      setIsWatchListGettingLoading(false);
    }
  }, [user?.user_id, user?.access_token]);

  const fetchSingleWatchList = useCallback(async (data) => {

    setIssingleWatchListGettingLoading(true);
    setGetsingleWatchListError(null);

    try {
      const response = await axiosInstance.get(`/watchlist/get/${data}`);
      setsingleWatchLists(response.data);
    } catch (error) {
      setGetsingleWatchListError(
        error.response?.data?.detail || "Failed to fetch watchlists. Please try again later."
      );
    } finally {
      setIssingleWatchListGettingLoading(false);
    }
  }, []);

  const createWatchlist = useCallback(async (data) => {

    try {
      const requestData = { ...data, owner: user?.user_id, access_token: user.access_token };
      const response = await axiosInstance.post(`/watchlist/create`, requestData);
      setWatchLists((prev) => (prev ? [...prev, response.data] : [response.data]));
    } catch (error) {
      console.error("Error creating watchlist:", error.response?.data?.detail || error.message);
    }
  }, [user?.user_id,user?.access_token]);
  
  const addMovieToWatchlist =  useCallback(async (watchlistId, movieId) => {
    try {
    const response  = await axiosInstance.post(`/watchlist/add_movie`, { watchlist_id: watchlistId, movie_id: movieId, access_token: user.access_token , user_id: user.user_id});
    return response.status;

    } catch (error) {
      console.error("Error adding movie to watchlist:", error?.detail);
      throw new Error(error?.detail || "Failed to add movie to watchlist");
    }

  }, [fetchUserWatchlists,user?.access_token,user?.user_id]);
  
  const deleteMovieFromWatchlist = useCallback(async (watchlistId, movieId) => {
    try {
      await axiosInstance.delete(`/watchlist/delete_movie/${user.user_id}/${watchlistId}/${movieId}/${user.access_token}`);
      // Update local state (optional: fetch updated watchlist data)
      fetchUserWatchlists();
      getGuestWatchlists(user?.user_id, user?.access_token)
    } catch (error) {
      console.error("Error deleting movie from watchlist:", error.response?.data?.detail || error.message);
    }
  }, [fetchUserWatchlists,user?.access_token, user?.user_id]);
  
  const deleteWatchlist = useCallback(async (watchlistId) => {
    try {
      await axiosInstance.delete(`/watchlist/delete/${watchlistId}/${user.access_token}`);
      setWatchLists((prev) => prev?.filter((watchlist) => watchlist.watchlist_id !== watchlistId) || []);
    } catch (error) {
      console.error("Error deleting watchlist:", error.response?.data?.detail || error.message);
    }
  }, [user?.access_token]);
  
  const getMoviesInWatchlist = useCallback(async (watchlistId) => {
    try {
      const response = await axiosInstance.get(`/watchlist/get_movies/${watchlistId}`);
      return response.data.movies;
    } catch (error) {
      console.error("Error fetching movies in watchlist:", error.response?.data?.detail || error.message);
      return [];
    }
  }, []);
  
  const updateWatchlist = useCallback(async (data) => {
    try {
      const requestData = { ...data, owner: user?.user_id, access_token: user.access_token };
      const response = await axiosInstance.put(`/watchlist/update`, requestData);
      setWatchLists((prev) =>
        prev?.map((watchlist) =>
          watchlist.watchlist_id === response.data.watchlist_id ? response.data : watchlist
        ) || []
      );
    } catch (error) {
      console.error("Error updating watchlist:", error.response?.data?.detail || error.message);
    }
  }, [user?.user_id,user?.access_token]);
  
  const getSingleMovie = useCallback(async (movie_id) => {
    setIsSingleMovieLoading(true);
    setSingleMovieError(null);
  
    try {
      const response = await axiosInstance.get(`/movie/get/${movie_id}`);
      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to fetch movie. Please try again later.";
      setSingleMovieError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSingleMovieLoading(false);
    }
  }, []);
  
const getGenres = useCallback(async () => {
  setIsGenresLoading(true);
  setGenresError(null);

  try {
    const response = await axiosInstance.get("/movie/get_genres");
    return response.data;
  } catch (error) {
    const errorMessage =
      error.response?.data?.detail || "Failed to fetch genres. Please try again later.";
    setGenresError(errorMessage);
    return []
  } finally {
    setIsGenresLoading(false);

  }
}, []);


const fetchSearchedMovies = useCallback(
  async ({
    substring = null,
    release_date = null,
    min_rating = null,
    genres = [],
    sort_by = "rating",
    page = 1,
  } = {}) => {
    setIssearchmoviesLoading(true);
    setsearchmoviesError(null);

//     function paramsSerializer(params) {
//   const parts = [];
//   for (const key in params) {
//     const value = params[key];
//     if (Array.isArray(value)) {
//       value.forEach(v => {
//         parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
//       });
//     } else if (value !== undefined && value !== null) {
//       parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
//     }
//   }
//   return parts.join("&");
// }

    try {
      const body = {
      ...(substring !== null ? { substring } : {}),
      ...(release_date !== null ? { release_date } : {}),
      ...(min_rating !== null ? { min_rating } : {}),
      ...(genres.length > 0 ? { genres } : {}),
      ...(sort_by !== null ? { sort_by } : {}),
      ...(page !== null ? { page } : {}),
    };

      const response = await axiosInstance.post("/movie/search", body);

      setsearchmovies(response.data['results']);
      setsearchtotalpages(response.data['totalPages']);
    } catch (error) {
      const errorMessage =
        error.detail || "Failed to fetch movies. Please try again later.";
      setsearchmoviesError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIssearchmoviesLoading(false);
    }
  },
  []
);


const getGuestWatchlists = useCallback(async (user_id, access_token) => {
  try {
    const response = await axiosInstance.get(`/watchlist/get_all_guests_watchlists/${user_id}/${access_token}`);
    setguest_watchlists(response.data.watchlists);
  } catch (error) {
    console.error("Error fetching guest watchlists:", error.response?.data?.detail || error.message);
    throw new Error(error.response?.data?.detail || "Failed to fetch guest watchlists.");
  }
}, []);

const removeGuestFromWatchlist = useCallback(
  async (watchlistId, user_id, access_token) => {
    try {
      await axiosInstance.delete(`/watchlist/remove_guest/${watchlistId}/${user_id}/${access_token}`);
      setguest_watchlists((prev) =>
        prev?.filter((watchlist) => watchlist.watchlist_id !== watchlistId) || []
      );
    } catch (error) {
      console.error("Error removing guest from watchlist:", error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || "Failed to leave the watchlist.");
    }
  },
  []
);

const searchWatchlists = useCallback(async (substring, username) => {
  try {
    const response = await axiosInstance.get(`/watchlist/search/${substring}/${username}`);
    return response.data.watchlists;
  } catch (error) {
    console.error("Error searching watchlists:", error.response?.data?.detail || error.message);
    throw new Error(error.response?.data?.detail || "Failed to search watchlists.");
  }
}, []);

// const addGuestToWatchlist = useCallback(async (watchlist_id, user_id, access_token,role) => {
//   try {
//     const response = await axiosInstance.post(`/watchlist/add_guest`, {
//       watchlist_id,
//       user_id,
//       access_token,
//       role: role.toUpperCase()
//     });
//     return response.data;
//   } catch (error) {
//     console.error("Error adding guest to watchlist:", error.response?.data?.detail || error.message);
//     throw new Error(error.response?.data?.detail || "Failed to join the watchlist.");
//   }
// }, []);

const createRecommendation = useCallback(
  async (movieId, recommendedUsername)=> {
    if (!user?.user_id) {
      throw new Error("User must be logged in to recommend movies.");
    }

    try {
      await axiosInstance.post("/users/recommendation/create", {
        recommender: user.user_id,
        recommended: recommendedUsername,
        movie_id: movieId,
        access_token: user.access_token
      });
    } catch (error) {
      console.error(error.detail);
      throw new Error(error.detail);
    }
  },
  [user]
);

const fetchRecommendationsForUser = async (username, access_token) => {
  try {
    const response = await axiosInstance.get(`/users/recommendation/get/${username}/${access_token}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching recommendations:", error.response?.data || error.message);
    throw new Error("Failed to fetch recommendations");
  }
};

const [isUpdatingLoading, setIsUpdatingLoading] = useState(false);
const [updateError, setUpdateError] = useState(null);

const updateUserToMovie = useCallback(
  async (
    user_id = user?.user_id,
    access_token  = user?.access_token,
    movie_id,
    times_watched = 0,
    has_watched = false,
    is_favorite = false,
    watching_now = false,
    rating = 0.0
  ) => {
    setIsUpdatingLoading(true);
    setUpdateError(null);

    try {
      const response = await axiosInstance.post("movie/actions", {
        user_id: user_id,
        movie_id: movie_id,
        access_token: access_token,
        times_watched,
        has_watched,
        is_favorite,
        watching_now,
        rating,
      });
      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to update user-movie relation.";
      setUpdateError(errorMessage);
      return null;
    } finally {
      setIsUpdatingLoading(false);
    }
  },
  []
);

const [isFetchingUserMovieInfo, setIsFetchingUserMovieInfo] = useState(false);
const [fetchUserMovieError, setFetchUserMovieError] = useState(null);

const getUserToMovieInfo = useCallback(
  async (user_id, access_token, movie_id) => {
    setIsFetchingUserMovieInfo(true);
    setFetchUserMovieError(null);

    try {
      const response = await axiosInstance.get("movie/actions", {
        params: {
          user_id,
          access_token,
          movie_id,
        },
      });

      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to fetch user-movie info.";
      setFetchUserMovieError(errorMessage);
      return {};
    } finally {
      setIsFetchingUserMovieInfo(false);
    }
  },
  []
);

const [isFetchingRecommendation, setIsFetchingRecommendation] = useState(false);
const [fetchRecommendationError, setFetchRecommendationError] = useState(null);

const getMovieRecommendations = useCallback(
  async (movie_id) => {
    setIsFetchingRecommendation(true);
    setFetchRecommendationError(null);

    try {
      const response = await axiosInstance.get(`/movie/get_movie_recommendation/${movie_id}`);
      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to fetch movie recommendations.";
      setFetchRecommendationError(errorMessage);
      return {};
    } finally {
      setIsFetchingRecommendation(false);
    }
  },
  []
);

const [isFetchingWatchlistRecommendations, setIsFetchingWatchlistRecommendations] = useState(false);
const [fetchWatchlistRecommendationError, setFetchWatchlistRecommendationError] = useState(null);

const getWatchlistRecommendations = useCallback(
  async (watchlist_id) => {
    setIsFetchingWatchlistRecommendations(true);
    setFetchWatchlistRecommendationError(null);

    try {
      const response = await axiosInstance.get(`/watchlist/get_movie_recommendation/${watchlist_id}`);
      return response.data;
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to fetch watchlist recommendations.";
      setFetchWatchlistRecommendationError(errorMessage);
      return {};
    } finally {
      setIsFetchingWatchlistRecommendations(false);
    }
  },
  []
);

const [isFetchingGuests, setIsFetchingGuests] = useState(false);
const [fetchGuestsError, setFetchGuestsError] = useState(null);

const getAllGuests = useCallback(async (watchlist_id) => {
  setIsFetchingGuests(true);
  setFetchGuestsError(null);

  try {
    const response = await axiosInstance.get(`/watchlist/all_guests/${watchlist_id}`);
    return response.data;
  } catch (error) {
    const errorMessage =
      error.response?.data?.detail || "Failed to fetch guests for this watchlist.";
    setFetchGuestsError(errorMessage);
    return null;
  } finally {
    setIsFetchingGuests(false);
  }
}, []);

const [isUpdatingGuest, setIsUpdatingGuest] = useState(false);
const [updateGuestError, setUpdateGuestError] = useState(null);

const updateGuestPermissions = useCallback(async (data) => {
  setIsUpdatingGuest(true);
  setUpdateGuestError(null);

  try {
    const response = await axiosInstance.post(`/watchlist/update_guest`, data);
    return response.data;
  } catch (error) {
    const errorMessage =
      error.response?.data?.detail || "Failed to update guest permissions.";
    setUpdateGuestError(errorMessage);
    return null;
  } finally {
    setIsUpdatingGuest(false);
  }
}, []);

  return (
<MovieContext.Provider
  value={{
    movies,
    searchInfo,
    updateSearchInfo,
    fetchMovies,
    getMovieError,
    isMovieGettingLoading,
    isWatchListGettingLoading,
    getWatchListError,
    watchlists,
    fetchUserWatchlists,
    createWatchlist,
    addMovieToWatchlist,
    deleteMovieFromWatchlist,
    deleteWatchlist,
    getMoviesInWatchlist,
    updateWatchlist,
    IsSingleMovieLoading,
    SingleMovieError,
    getSingleMovie,
    // reviews,
    // reviewError,
    // isReviewLoading,
    // fetchReviewsForMovie,
    // createReview,
    // updateReview,
    // deleteReview,
    getGuestWatchlists,
    guest_watchlists,
    removeGuestFromWatchlist,
    searchWatchlists,
    //addGuestToWatchlist,
    createRecommendation,
    fetchRecommendationsForUser,
    singlewatchlists,
    issingleWatchListGettingLoading,
    fetchSingleWatchList,
    getsingleWatchListError,
    getGenres,
    fetchSearchedMovies,
    searchmovies,
    searchmoviesError,
    issearchmoviesLoading,
    totalPages,
    updateUserToMovie,
    getUserToMovieInfo, getMovieRecommendations, getWatchlistRecommendations, updateGuestPermissions, getAllGuests


  }}
>
  {children}
</MovieContext.Provider>

  );
};

export const useMovieContext = () => {
  const context = useContext(MovieContext);
  if (!context) {
    throw new Error("useMovieContext must be used within a MovieContextProvider");
  }
  return context;
};

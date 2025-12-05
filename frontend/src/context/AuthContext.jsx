import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { axiosInstance } from "../utils/axiosHelper";
import { useNavigate } from "react-router-dom";
import { jwtDecode  } from 'jwt-decode';
export const AuthContext = createContext(undefined);

export const AuthContextProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [registerError, setRegisterError] = useState(null);
    const [isRegisterLoading, setIsRegisterLoading] = useState(false);
    const [registerInfo, setRegisterInfo] = useState({
        username: "",
        email: "",
        password: "",
        confirmpassword: "",
    });
    const navigate = useNavigate();

    const [LoginError, setLoginError] = useState(null);
    const [isLoginLoading, setIsLoginLoading] = useState(false);
    const [loginInfo, setLoginInfo] = useState({
        username: "",
        password: "",
    });

    const [verifyInfo, setverifyInfo] = useState({});
    const [verifyloading, setverifyloading] = useState(false);
    const [verifyError, setverifyError] = useState(null)
    const [showVerify, setshowVerify] = useState(false)
    const [friends, setFriends] = useState(null);
    const [friendError, setFriendError] = useState(null);
    const [isFriendLoading, setIsFriendLoading] = useState(false);

    const [friendRequestError, setFriendRequestError] = useState(null);
    const [isFriendRequestLoading, setIsFriendRequestLoading] = useState(false);

    const [removeFriendError, setRemoveFriendError] = useState(null);
    const [isRemoveFriendLoading, setIsRemoveFriendLoading] = useState(false);

    useEffect(() => {
        const storedUser = localStorage.getItem("User");
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    useEffect(() => {
    
        if (user && user.access_token) {
          try {
            const decodedToken = jwtDecode(user.access_token);
            const currentTime = Number(Date.now() / 1000); 

            if (decodedToken.exp < currentTime) {
                localStorage.removeItem("User");
                navigate("/");
                setUser(null);
            }
          } catch (error) {
            console.error('Error decoding token:', error);
          }
        }
      }, [user,navigate]);

    const updateRegisterInfo = useCallback((info) => {
        setRegisterInfo(info);
    }, []);

    const registerUser = useCallback(
        async (e) => {
            e.preventDefault();
            setIsRegisterLoading(true);
            setRegisterError(null);
            if (registerInfo.username.length < 6) {
                setRegisterError("Username must be at least 6 characters long.");
                setIsRegisterLoading(false);
                return;
            }
            if (registerInfo.password.length < 8) {
                setRegisterError("Password must be at least 8 characters long.");
                setIsRegisterLoading(false);
                return;
            }
    
            try {
                const response = await axiosInstance.post("/users/register", registerInfo);
                setIsRegisterLoading(false);

                // Save user data
                //localStorage.setItem("User", JSON.stringify(response.data));
                //setUser(response.data);
                setverifyInfo(response.data);
                setshowVerify(true)
            } catch (error) {
                setIsRegisterLoading(false);
                setRegisterError(error?.detail || "Registration failed.");
            }
        },
        [registerInfo]
    );

    const logoutUser = useCallback(() => {
        localStorage.removeItem("User");
        navigate("/");
        setUser(null);
    }, []);

    const loginUser = useCallback(
        async (e) => {
            e.preventDefault();
            setIsLoginLoading(true);
            setLoginError(null);
            if (loginInfo.username.length < 6) {
                setLoginError("Invalid username or password.");
                setIsLoginLoading(false);
                return;
            }
            if (loginInfo.password.length < 8) {
                setLoginError("Invalid username or password.");
                setIsLoginLoading(false);
                return;
            }
            try {
                const response = await axiosInstance.post("/users/login", loginInfo);
                setIsLoginLoading(false);

                // Save user data
                //localStorage.setItem("User", JSON.stringify(response.data));
                setverifyInfo(response.data);
                setshowVerify(true)
            } catch (error) {
                setIsLoginLoading(false);
                setLoginError(error?.detail || "Login failed.");
            }
        },
        [loginInfo]
    );

const VerifyLoginUser = useCallback(
  async (info) => {
    setverifyloading(true);
    setverifyError("");

    try {
      const response = await axiosInstance.post("/users/verify", info);

      localStorage.setItem("User", JSON.stringify(response.data));
      setUser(response.data);
      setverifyInfo({})
      setshowVerify(false)
    } catch (error) {
      const message =
        error.detail ||
        "Login failed.";
      setverifyError(message);
    } finally {
      setverifyloading(false);
    }
  },
  [setUser, setverifyloading, setverifyError]
);


    const updateLoginInfo = useCallback((info) => {
        setLoginInfo(info);
    }, []);

    const fetchFriends = useCallback(async () => {
        if (!user) {
            setFriendError("User is not logged in.");
            return;
        }
        setIsFriendLoading(true);
        setFriendError(null);
        try {
            const response = await axiosInstance.get(`/users/friends/get_all/${user.user_id}/${user.access_token}`);
            setFriends(response.data.friends);
            return response.data.friends
        } catch (error) {
            setFriendError(error?.detail || "Failed to fetch friends.");
        } finally {
            setIsFriendLoading(false);
        }
    }, [user]);

    //   const fetchFriendsNonAsync =  (user) => {
    //     if (!user) {
    //         setFriendError("User is not logged in.");
    //         return;
    //     }
    //     setIsFriendLoading(true);
    //     setFriendError(null);
    //     try {
    //         const response = axiosInstance.get(`/users/friends/get_all/${user.user_id}/${user.access_token}`);
    //         setFriends(response.data.friends);
    //     } catch (error) {
    //         setFriendError(error?.detail || "Failed to fetch friends.");
    //     } finally {
    //         setIsFriendLoading(false);
    //     }
    // };

    const sendFriendRequest = async (friendUsername) => {
        if (!user) return;
    
        try {
            const response = await axiosInstance.post("/users/friends/request", {
                user_one: user.user_id,
                user_two: friendUsername,
                access_token: user.access_token
            });
            return response;
        } catch (error) {
            throw error.response || new Error("Failed to send friend request");
        }
    };

    const removeFriend = useCallback(
        async (friendUsername) => {
            if (!user) return;

            setIsRemoveFriendLoading(true);
            setRemoveFriendError(null);

            try {
                await axiosInstance.delete(`/users/friends/remove/${user.user_id}/${friendUsername}/${user.access_token}`);
                setFriends((prev) => prev?.filter((friend) => friend.user_id !== friendUsername) || null);
            } catch (error) {
                setRemoveFriendError(error?.response?.data?.detail || "Failed to remove friend.");
            } finally {
                setIsRemoveFriendLoading(false);
            }
        },
        [user]
    );


    const [userMovieActions, setUserMovieActions] = useState(null);
    const [isLoadingActions, setIsLoadingActions] = useState(false);
    const [actionsError, setActionsError] = useState(null);

    const fetchUserMovieActions = useCallback(async (user_to_movie) => {
        if (!user_to_movie) return;

        setIsLoadingActions(true);
        setActionsError(null);

        try {
            const response = await axiosInstance.get(`/movie/get_all_actions`, {
                params: {
                    user_id: user_to_movie.user_id,
                    //access_token: user_to_movie.access_token
                }
            });
            setUserMovieActions(response.data);
        } catch (error) {
            setActionsError(
                error?.response?.data?.detail || "Failed to fetch movie actions."
            );
        } finally {
            setIsLoadingActions(false);
        }
    });
    return (
        <AuthContext.Provider
            value={{
                user,
                registerInfo,
                updateRegisterInfo,
                registerUser,
                registerError,
                isRegisterLoading,
                logoutUser,
                loginInfo,
                updateLoginInfo,
                loginUser,
                LoginError,
                isLoginLoading,
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
                fetchUserMovieActions,
                userMovieActions,
                isLoadingActions,
                actionsError,
                VerifyLoginUser,
                showVerify,
                setshowVerify,
                verifyError,
                verifyloading,
                verifyInfo,
                setverifyInfo,
                setverifyError
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuthContext = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuthContext must be used within an AuthContextProvider");
    }
    return context;
};

import { useContext } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import { AuthContext } from "./context/AuthContext";
import MoviesPage from "./pages/Movies";
import MovieDetailsPage from "./pages/SIngleMovie";
import WatchlistPage from "./pages/WatchList";
import FriendsPage from "./pages/Friends";
import SearchMoviesPage from "./pages/SearchMovies";
import UserPage from "./pages/UserPage";
import './index.css';

const App = () => {
    const authContext = useContext(AuthContext);

    if (!authContext) {
        throw new Error("AuthContext must be used within an AuthContextProvider");
    }

    const { user } = authContext;

    return (
        <Routes>
            <Route path="/" element={user ? <MoviesPage /> : <LoginPage />} />
            <Route path="/register" element={user ? <MoviesPage /> : <RegisterPage />} />
            <Route path="/login" element={user ? <MoviesPage /> : <LoginPage />} />
            <Route path="*" element={<Navigate to="/" />} />
            <Route path="/movie/:id" element={<MovieDetailsPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/search-movies" element={<SearchMoviesPage />} />
            <Route path="/profile/:user_id" element={<UserPage />} />

            {/* <Route path="/events" element={<EventsPage />} /> */}
            <Route path="/friends" element={<FriendsPage />} />
        </Routes>
    );
};

export default App;

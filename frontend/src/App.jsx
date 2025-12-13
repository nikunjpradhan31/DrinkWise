// src/App.jsx
import { useContext } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthContext } from "./context/AuthContext";
import NavBar from "./components/NavBar";

import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import LandingPage from "./pages/Landing";
import DrinkPage from "./pages/DrinkPage";
import AccountPage from "./pages/Account";
import TasteQuizPage from "./pages/TasteQuiz";
import SearchPage from "./pages/Search";

const App = () => {
  const auth = useContext(AuthContext);
  if (!auth) {
    throw new Error("AuthContext must be used within AuthContextProvider");
  }
  const { user } = auth;
  console.log(user);
  const PrivateRoute = (Component) =>
    user ? <Component /> : <Navigate to="/login" replace />;

  const PreferenceRoute = (Component) => {
    if (!user) {
      return <Navigate to="/login" replace />;
    }
    
    // If user has finished preferences, go to dashboard
    if (user.preference_finished) {
      return <Navigate to="/" replace />;
    }
    
    // Otherwise, show the component (Taste Quiz)
    return <Component />;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {user && <NavBar />}
      <div className={user ? "pt-16" : ""}>
        <Routes>
        <Route
          path="/"
          element={user ? (
            user.preference_finished ? <LandingPage /> : <Navigate to="/taste-quiz" replace />
          ) : <Navigate to="/login" replace />}
        />
        <Route
          path="/login"
          element={!user ? <LoginPage /> : (
            user.preference_finished ? <Navigate to="/" replace /> : <Navigate to="/taste-quiz" replace />
          )}
        />
        <Route
          path="/register"
          element={!user ? <RegisterPage /> : (
            user.preference_finished ? <Navigate to="/" replace /> : <Navigate to="/taste-quiz" replace />
          )}
        />
        <Route path="/taste-quiz" element={PreferenceRoute(TasteQuizPage)} />
        <Route path="/search" element={PrivateRoute(SearchPage)} />
        <Route path="/drink/:id" element={PrivateRoute(DrinkPage)} />
        <Route path="/account" element={PrivateRoute(AccountPage)} />
        <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;

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

const App = () => {
  const auth = useContext(AuthContext);
  if (!auth) {
    throw new Error("AuthContext must be used within AuthContextProvider");
  }
  const { user } = auth;

  const PrivateRoute = (Component) =>
    user ? <Component /> : <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {user && <NavBar />}
      <Routes>
        <Route
          path="/"
          element={user ? <LandingPage /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/login"
          element={!user ? <LoginPage /> : <Navigate to="/" replace />}
        />
        <Route
          path="/register"
          element={!user ? <RegisterPage /> : <Navigate to="/" replace />}
        />
        <Route path="/drink/:id" element={PrivateRoute(DrinkPage)} />
        <Route path="/account" element={PrivateRoute(AccountPage)} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
};

export default App;

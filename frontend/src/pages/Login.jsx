// src/pages/Login.jsx
import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import ForgotPassword from "../components/ForgotPassword";

const LoginPage = () => {
  const auth = useContext(AuthContext);
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  if (!auth) throw new Error("AuthContext missing");
  const { loginUser, authLoading } = auth;

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await loginUser({
        username: form.username,
        password: form.password,
      });
      navigate("/");
    } catch (err) {
      setError(
        err?.message || err?.error || "Invalid username or password."
      );
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="w-full max-w-md bg-slate-900/70 border border-slate-700/60 rounded-2xl p-6 shadow-xl">
        <h1 className="text-xl font-semibold text-white mb-4">
          Login to DrinkWise
        </h1>
        {error && (
          <p className="mb-3 text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-slate-300 mb-1">
              Username
            </label>
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-xs text-slate-300 mb-1">
              Password
            </label>
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="text-xs text-blue-200 hover:underline"
            >
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            disabled={authLoading}
            className="w-full mt-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
          >
            {authLoading ? "Logging in…" : "Login"}
          </button>
        </form>

        <p className="mt-4 text-xs text-slate-400">
          Don't have an account?{" "}
          <Link to="/register" className="text-blue-200 hover:underline">
            Register here
          </Link>
        </p>
      </div>

      {showForgotPassword && (
        <ForgotPassword onClose={() => setShowForgotPassword(false)} />
      )}
    </div>
  );
};

export default LoginPage;

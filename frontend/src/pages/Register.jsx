// src/pages/Register.jsx
import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import TasteQuizForm from "../components/TasteQuizForm";

const RegisterPage = () => {
  const auth = useContext(AuthContext);
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmpassword: "",
    date_of_birth: "",
  });
  const [error, setError] = useState("");
  const [showQuiz, setShowQuiz] = useState(false);

  if (!auth) throw new Error("AuthContext missing");
  const { registerUser, authLoading, fetchMe } = auth;

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmpassword) {
      setError("Passwords do not match.");
      return;
    }

    const payload = {
      username: form.username,
      email: form.email,
      password: form.password,
      confirmpassword: form.confirmpassword,
      date_of_birth: form.date_of_birth
        ? new Date(form.date_of_birth).toISOString()
        : null,
    };

    try {
      await registerUser(payload);
      setShowQuiz(true);
    } catch (err) {
      setError(err?.message || err?.error || "Registration failed.");
    }
  };

  const handleQuizCompleted = async () => {
    try {
      await fetchMe();
    } catch (e) {
      console.error(e);
    }
    navigate("/");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="w-full max-w-md bg-slate-900/70 border border-slate-700/60 rounded-2xl p-6 shadow-xl space-y-4">
        {!showQuiz ? (
          <>
            <h1 className="text-xl font-semibold text-white">
              Create a DrinkWise account
            </h1>
            {error && (
              <p className="mb-1 text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
                {error}
              </p>
            )}

            <form
              onSubmit={handleRegisterSubmit}
              className="space-y-4 mt-2"
            >
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
                  Email
                </label>
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Date of Birth (optional)
                </label>
                <input
                  name="date_of_birth"
                  type="date"
                  value={form.date_of_birth}
                  onChange={handleChange}
                className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
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

              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Confirm Password
                </label>
                <input
                  name="confirmpassword"
                  type="password"
                  value={form.confirmpassword}
                  onChange={handleChange}
                className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

              <button
                type="submit"
                disabled={authLoading}
                className="w-full mt-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
              >
                {authLoading ? "Creating account…" : "Continue to taste quiz"}
              </button>
            </form>

            <p className="mt-2 text-xs text-slate-400">
              Already have an account?{" "}
              <Link to="/login" className="text-blue-200 hover:underline">
                Login here
              </Link>
            </p>
          </>
        ) : (
          <>
            <h1 className="text-xl font-semibold text-white mb-1">
              Tell us your taste
            </h1>
            <p className="text-xs text-slate-400 mb-2">
              Thanks for signing up! Answer a few quick questions so we can
              personalize your recommendations.
            </p>
            <TasteQuizForm onCompleted={handleQuizCompleted} />
          </>
        )}
      </div>
    </div>
  );
};

export default RegisterPage;

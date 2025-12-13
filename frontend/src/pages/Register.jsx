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
  const [validationErrors, setValidationErrors] = useState({});

  if (!auth) throw new Error("AuthContext missing");
  const { registerUser, authLoading, fetchMe } = auth;

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const validateForm = () => {
    const errors = {};

    // Username validation
    if (!form.username.trim()) {
      errors.username = "Username is required";
    } else if (form.username.length < 3) {
      errors.username = "Username must be at least 3 characters";
    } else if (form.username.length > 50) {
      errors.username = "Username must be less than 50 characters";
    }

    // Email validation
    if (!form.email.trim()) {
      errors.email = "Email is required";
    } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
      errors.email = "Please enter a valid email address";
    }

    // Password validation
    if (!form.password) {
      errors.password = "Password is required";
    } else if (form.password.length < 8) {
      errors.password = "Password must be at least 8 characters";
    } else if (!/[A-Z]/.test(form.password)) {
      errors.password = "Password must contain at least one uppercase letter";
    } else if (!/[a-z]/.test(form.password)) {
      errors.password = "Password must contain at least one lowercase letter";
    } else if (!/[0-9]/.test(form.password)) {
      errors.password = "Password must contain at least one number";
    } else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(form.password)) {
      errors.password = "Password must contain at least one special character";
    }

    // Confirm password validation
    if (form.password !== form.confirmpassword) {
      errors.confirmpassword = "Passwords do not match";
    }

    // Date of birth validation (if provided)
    if (form.date_of_birth) {
      const dob = new Date(form.date_of_birth);
      const today = new Date();
      const minAgeDate = new Date(today.getFullYear() - 13, today.getMonth(), today.getDate());

      if (dob > minAgeDate) {
        errors.date_of_birth = "You must be at least 13 years old";
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) {
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
                className={`w-full rounded-md bg-slate-900 border ${validationErrors.username ? 'border-red-500' : 'border-slate-700'} px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              />
              {validationErrors.username && (
                <p className="text-xs text-red-400 mt-1">{validationErrors.username}</p>
              )}
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
                className={`w-full rounded-md bg-slate-900 border ${validationErrors.email ? 'border-red-500' : 'border-slate-700'} px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              />
              {validationErrors.email && (
                <p className="text-xs text-red-400 mt-1">{validationErrors.email}</p>
              )}
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
                className={`w-full rounded-md bg-slate-900 border ${validationErrors.date_of_birth ? 'border-red-500' : 'border-slate-700'} px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
              {validationErrors.date_of_birth && (
                <p className="text-xs text-red-400 mt-1">{validationErrors.date_of_birth}</p>
              )}
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
                className={`w-full rounded-md bg-slate-900 border ${validationErrors.password ? 'border-red-500' : 'border-slate-700'} px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              />
              {validationErrors.password && (
                <p className="text-xs text-red-400 mt-1">{validationErrors.password}</p>
              )}
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
                className={`w-full rounded-md bg-slate-900 border ${validationErrors.confirmpassword ? 'border-red-500' : 'border-slate-700'} px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              />
              {validationErrors.confirmpassword && (
                <p className="text-xs text-red-400 mt-1">{validationErrors.confirmpassword}</p>
              )}
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

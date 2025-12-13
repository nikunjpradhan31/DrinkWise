// src/pages/TasteQuiz.jsx
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { axiosInstance } from "../utils/axiosHelper";
import PreferenceForm from "../components/PreferenceForm";

const TasteQuizPage = () => {
  const auth = useContext(AuthContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  if (!auth) throw new Error("AuthContext missing");
  const { user, fetchMe } = auth;

  useEffect(() => {
    const checkUser = async () => {
      try {
        // If user is already logged in and has preferences finished, redirect to dashboard
        if (user && user.preference_finished) {
          navigate("/");
          return;
        }
        
        // If user is logged in but we need to check their latest status
        if (user) {
          if (user && user.preference_finished) {
              navigate("/");
              return;
            }

        }
      } catch (err) {
        console.error("Error checking user preferences:", err);
        setError("Failed to load your preferences. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    checkUser();
  }, [user, fetchMe, navigate]);

  const handleQuizCompleted = async () => {
    try {
      // Update user profile to mark preferences as finished
      await axiosInstance.put("/auth/me", {
        preference_finished: true
      });
      
      // Refresh user data
      await fetchMe();
      
      // Redirect to dashboard
      navigate("/");
    } catch (err) {
      console.error("Error completing quiz:", err);
      setError("Failed to save your preferences. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        Loading your taste quiz…
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        <div className="text-center space-y-4">
          <h1 className="text-xl font-semibold">Error Loading Taste Quiz</h1>
          <p className="text-sm text-red-400">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="w-full max-w-md bg-slate-900/70 border border-slate-700/60 rounded-2xl p-6 shadow-xl space-y-4">
        <h1 className="text-xl font-semibold text-white">
          Welcome to DrinkWise!
        </h1>
        <p className="text-sm text-slate-300">
          Set your drink preferences so we can recommend the perfect drinks for you.
        </p>
        <PreferenceForm onCompleted={handleQuizCompleted} />
      </div>
    </div>
  );
};

export default TasteQuizPage;
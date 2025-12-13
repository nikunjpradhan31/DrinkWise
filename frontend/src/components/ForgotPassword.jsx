// src/components/ForgotPassword.jsx
import { useState } from "react";
import { axiosInstance } from "../utils/axiosHelper";

const ForgotPassword = ({ onClose }) => {
  const [step, setStep] = useState(1); // 1 = email request, 2 = reset form
  const [email, setEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await axiosInstance.post("/auth/request-password-reset", {
        email: email
      });
      
      setSuccess("If the email exists, a password reset link has been sent.");
      setStep(2);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to request password reset.");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    try {
      const response = await axiosInstance.post("/auth/forgot-password", {
        email: email,
        verification_code: verificationCode,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      
      setSuccess("Password reset successfully! You can now login with your new password.");
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to reset password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900/90 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">
            {step === 1 ? "Forgot Password" : "Reset Password"}
          </h2>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-slate-400 hover:text-white disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-sm text-red-300">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-green-900/30 border border-green-700 rounded-lg text-sm text-green-300">
            {success}
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleRequestReset} className="space-y-4">
            <p className="text-sm text-slate-300">
              Enter your email address and we'll send you a verification code to reset your password.
            </p>
            
            <div>
              <label className="block text-xs text-slate-300 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
            >
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>
        ) : (
          <form onSubmit={handlePasswordReset} className="space-y-4">
            <p className="text-sm text-slate-300">
              We've sent a verification code to {email}. Enter it below along with your new password.
            </p>

            <div>
              <label className="block text-xs text-slate-300 mb-1">Verification Code</label>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                className="w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-xs text-slate-300 mb-1">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                minLength={8}
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-xs text-slate-300 mb-1">Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                minLength={8}
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md transition-colors"
            >
              {loading ? "Resetting..." : "Reset Password"}
            </button>
          </form>
        )}

        <button
          onClick={() => setStep(1)}
          className={`mt-4 text-xs text-slate-400 hover:text-slate-200 ${step === 1 ? 'invisible' : ''}`}
          disabled={loading}
        >
          Back to email entry
        </button>
      </div>
    </div>
  );
};

export default ForgotPassword;
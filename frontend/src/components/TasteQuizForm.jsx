// src/components/TasteQuizForm.jsx
import { useEffect, useState } from "react";
import { axiosInstance } from "../utils/axiosHelper";

const TasteQuizForm = ({ onCompleted }) => {
  const [questions, setQuestions] = useState([]);
  const [selected, setSelected] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axiosInstance.get("/quiz/provide", {
          params: { count: 8 },
        });
        const data = res.data;
        setQuestions(data.questions || []);
      } catch (e) {
        console.error(e);
        setError(
          e?.message || e?.error || "Failed to load taste quiz questions."
        );
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  const handleSelect = (questionId, optionId) => {
    setSelected((prev) => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!questions.length) return;

    const unanswered = questions.filter(
      (q) => !selected[q.question_id]
    );
    if (unanswered.length > 0) {
      setError("Please answer all questions before submitting.");
      return;
    }

    const answers = questions.map((q) => ({
      question_id: q.question_id,
      option_id: selected[q.question_id],
    }));

    setSubmitting(true);
    try {
      const res = await axiosInstance.post("/quiz/submit", { answers });
      const data = res.data;
      onCompleted?.(data);
    } catch (e) {
      console.error(e);
      setError(e?.message || e?.error || "Failed to submit taste quiz.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p className="text-sm text-slate-300">Loading your taste quiz…</p>;
  }

  if (error && !questions.length) {
    return (
      <p className="text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
        {error}
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <p className="text-sm text-red-400 bg-red-950/30 px-3 py-2 rounded-lg">
          {error}
        </p>
      )}

      <p className="text-sm text-slate-300">
        Help us learn your drink preferences. Answer these quick questions so
        we can recommend drinks you&apos;ll actually enjoy.
      </p>

      <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
        {questions.map((q, index) => (
          <div
            key={q.question_id}
            className="rounded-lg bg-slate-900/70 border border-slate-700/70 p-3"
          >
            <p className="text-sm font-medium text-white mb-2">
              {index + 1}. {q.question_text}
            </p>
            <div className="space-y-1">
              {q.options.map((opt) => (
                <label
                  key={opt.option_id}
                  className="flex items-center gap-2 text-xs text-slate-200 cursor-pointer"
                >
                  <input
                    type="radio"
                    name={`question-${q.question_id}`}
                    value={opt.option_id}
                    checked={selected[q.question_id] === opt.option_id}
                    onChange={() =>
                      handleSelect(q.question_id, opt.option_id)
                    }
                    className="h-3 w-3 accent-purple-500"
                  />
                  <span>{opt.option_text}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium py-2.5 rounded-md mt-2 transition-colors"
      >
        {submitting ? "Submitting your tastes…" : "Finish and see recommendations"}
      </button>
    </form>
  );
};

export default TasteQuizForm;

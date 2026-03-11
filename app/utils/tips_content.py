"""Anxiety tips content — static fallback when Gemini is unavailable."""

ANXIETY_TIPS = {
    "Low Anxiety": {
        "color": "green",
        "emoji": "🟢",
        "message": "You seem to be managing well! Keep up the good work.",
        "tips": [
            "Continue your current study routine — it's working!",
            "Take short breaks every 45 minutes to stay refreshed.",
            "Stay hydrated and maintain a balanced diet before exams.",
            "Practice positive self-talk: remind yourself of past successes.",
            "Get 7–8 hours of sleep the night before the exam.",
        ],
    },
    "Moderate Anxiety": {
        "color": "yellow",
        "emoji": "🟡",
        "message": "You're experiencing some anxiety. That's normal — here are some strategies to help.",
        "tips": [
            "Try the 4-7-8 breathing technique: inhale 4s, hold 7s, exhale 8s.",
            "Break your study material into smaller, manageable chunks.",
            "Use the Pomodoro technique: 25 minutes study, 5 minutes break.",
            "Write down your worries on paper to externalize them.",
            "Visualize yourself succeeding in the exam — positive imagery helps.",
        ],
    },
    "High Anxiety": {
        "color": "red",
        "emoji": "🔴",
        "message": "You appear to be experiencing significant anxiety. Please consider the strategies below and reaching out for support.",
        "tips": [
            "Practice grounding: name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.",
            "Try progressive muscle relaxation — tense and release each muscle group.",
            "Speak to a trusted friend, family member, or counselor about how you're feeling.",
            "Remember: one exam does not define your worth or your future.",
            "Consider reaching out to your institution's counseling service for professional support.",
        ],
        "counselor_referral": True,
    },
}

DISCLAIMER = (
    "⚠️ Disclaimer: This tool provides general wellness suggestions only. "
    "It is NOT a medical or psychological diagnosis. If you are experiencing "
    "severe anxiety or distress, please contact a qualified mental health "
    "professional or your institution's counseling service."
)

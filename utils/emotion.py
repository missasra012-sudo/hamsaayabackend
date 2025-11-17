def detect_emotion(text):
    text = text.lower()

    if any(word in text for word in ["happy", "good", "great", "awesome"]):
        return "happy"
    elif any(word in text for word in ["sad", "upset", "down"]):
        return "sad"
    elif any(word in text for word in ["angry", "mad", "furious"]):
        return "angry"
    else:
        return "neutral"


def generate_reply(emotion, language="english"):
    
    replies = {
        "english": {
            "happy": "You look happy today! Keep smiling!",
            "sad": "I'm here with you. Everything will be okay.",
            "angry": "Take a deep breath... I'm with you.",
            "neutral": "Tell me more, I’m listening."
        },
        "hindi": {
            "happy": "Aaj aap bahut khush lag rahi ho!",
            "sad": "Tension mat lo, main yahin hoon.",
            "angry": "Gehri saans lo, sab theek ho jayega.",
            "neutral": "Aur batao, kya chal raha hai?"
        }
    }

    lang = replies.get(language.lower(), replies["english"])
    return lang.get(emotion, "Tell me more about how you feel.")

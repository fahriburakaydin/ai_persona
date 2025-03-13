# src/config.py

# Posting mode: "fixed" or "dynamic"
POSTING_MODE = "dynamic"
FIXED_POSTING_INTERVAL = "18:00"  # used if POSTING_MODE == "fixed"

# Content mix ratios (adjust as needed)
SELF_CONTENT_RATIO = 0.4  
THEMATIC_CONTENT_RATIO = 0.6

# Self-image handling mode: "preapproved", "generated", or "hybrid"
SELF_IMAGE_MODE = "hybrid"

# Engagement learning settings
ENGAGEMENT_UPDATE_INTERVAL = 24  # in hours
LEARNING_RATE = 0.1

# Autonomous posting triggers
MIN_POST_GAP_HOURS = 6          # minimum hours between posts
ENGAGEMENT_TRIGGER_THRESHOLD = 0.5  # placeholder for engagement-based decisions

# Intent detection threshold (for interactive console)
INTENT_CONFIDENCE_THRESHOLD = 0.45

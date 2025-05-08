## Autonomous AI Persona Template

### Introduction

This project is a **template for creating AI personas** that come to life through conversation and social media. Each persona features:

- **Dynamic Personality & Memory**
    - **Short-Term Memory:** Keeps track of recent exchanges to maintain conversational context.
    - **Long-Term Memory:** Summarizes and stores key insights over time for consistent character development.
- **Interactive Console:**
    - A CLI where users chat with the persona, give explicit feedback (e.g., `/feedback be less sarcastic`), and observe how Lia’s traits evolve.
- **Instagram Presence:**
    - Lia exists on Instagram as a “real” influencer.
    - She autonomously generates **post ideas**, crafts **captions**, creates images, and publishes on schedule.
    - Comment/like/follow features are available but should be used sparingly to avoid detection.

---

### What It Does & How It Works

1. **Initialization**
    - Loads a JSON profile (name, appearance, personality traits, backstory, communication style).
    - Instantiates memory managers and the personality engine.
2. **Conversational Flow**
    - **Intent Detection:** Zero-shot classifier routes input to chat, post, or feedback handlers.
    - **Response Generation:** Combines LLM output with memory context and trait weights to craft replies.

    ![image](https://github.com/user-attachments/assets/91bce563-1c21-4560-aa86-b50f9309d08c)

    
3. **Autonomous Posting**
    - **Chain of AI Agents:** A series of specialized modules (post planner, prompt engineer, image generator, Instagram bot) collaborate to fully automate content creation.
    - **Post Planning:** Every 6+ hours, `LiaManager` invokes `generate_weighted_post_plan()`.
    - **Prompt Engineering:** `generate_technical_prompt()` refines the idea into a detailed scene description.
    - **Image Generation:** `generate_image()` calls Hugging Face with retry/backoff, saves PNGs in `/images`, and returns the path.
    - **Draft & Approval:** Drafts are logged; after manual approval, `InstagramIntegration` publishes the post with retry logic and logs the result.
    
      ![image](https://github.com/user-attachments/assets/fd35a82e-9541-4273-8b60-e4a8f975086d)

    
4. **Feedback & Learning**
    - **Explicit Feedback:** `/feedback …` commands immediately tweak personality weights.
    - **Implicit Feedback:** Semantic analysis of user messages updates trait weights over time.
    - All feedback and memories are stored in ChromaDB for semantic retrieval and future corrections.

---

### Code Highlights

- **Managers**
    - `LiaManager`: Orchestrates scheduling, planning, image creation, and posting.
    - `MemoryManager`: Handles short-term queues, conversation summarization, and long-term storage.
    - `FeedbackManager` & `PersonalityManager`: Record corrections and evolve trait weights.
- **Database Layer**
    - ChromaDB collections for feedback, memories, and personality themes.
- **Utilities & Agents**
    - **Prompt Engineer:** Refines image ideas into vivid, model-ready scene descriptions.
    - **Image Generator Agent:** Manages HTTP calls with timeout, retries, and persistent `/images` storage.
    - **Instagram Bot Agent:** Session management, human-like delays, and retry logic for posts.
- **Robustness**
    - Python `logging` for structured logs.
    - Retry loops around all external API calls.
    - Persistent draft tracking via `post_tracker`.

---

### Project File Structure

| **Category** | **File Count** |
| --- | --- |
| Managers | 4 |
| Database | 2 |
| Tools | 2 |
| Utils | 12 |
| Models | 1 |
| Profiles | 1 |
| Config | 1 |

---

### Google Cloud Platform Integration

- **Containerization & Deployment:**
    - Docker image built and pushed to Google Container Registry.
    - Deployed on **Cloud Run** for fully managed, auto-scaling execution.
- **Scheduling:**
    - **Cloud Scheduler** triggers the autonomous posting manager at configurable intervals.
- **CI/CD Pipeline:**
    - **Cloud Build** automates Docker image builds and deploys to Cloud Run on each commit.
- **Security & Secrets:**
    - API keys and credentials stored in **Secret Manager** (not detailed here for sensitivity).

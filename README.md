🏠  Estate-AI
AI-Powered Real Estate Marketplace — Lahore
FastAPI · Groq LLaMA 3.3 · SQLite · Vanilla JS

📌  What is Estate-AI?
Estate-AI is a full-stack real estate marketplace built for Lahore, Pakistan. It combines a FastAPI backend, SQLite database, and an AI concierge named Zara — powered by Groq's LLaMA 3.3-70b model — that helps buyers find properties and assists sellers in listing them. The entire frontend is plain HTML/CSS/JS served directly through the backend, with no build step required.

✨  Features
•	Zara AI Chat — conversational property search in Urdu/English via Groq LLaMA 3.3-70b
•	Live Listings Page — filter by location, type, bedrooms, price; loads from real database
•	Seller Dashboard — add, edit, delete listings; view buyer inquiries
•	Buyer Search — full-text search with inquiry submission
•	Shared Auth System — phone-based login/signup persisted in localStorage across all pages
•	Add Property Modal — available on every page once signed in
•	WebSocket support — real-time AI chat streaming
•	Voice Input — Web Speech API mic button in Zara chat
•	Auto-seeded database — pre-loaded with Lahore property data on first run

🛠  Tech Stack
Layer	Technology	Purpose
AI / LLM	Groq — LLaMA 3.3-70b	Zara's conversational brain
Backend	FastAPI + Uvicorn	REST API + WebSocket server
Database	SQLite + custom ORM	Properties, inquiries, site visits
Frontend	HTML / Tailwind CSS / JS	6 pages, no build step
Auth	localStorage + phone-based	No passwords, cross-page session
Voice	Web Speech API	Browser-native mic input
Memory	JSON file store	Per-session user preferences

📁  Project Structure
real-estate/
├── agent.py              ← Zara AI brain (Groq + tool calls)
├── server.py             ← FastAPI server (REST + WebSocket + static files)
├── database.py           ← SQLite ORM (properties, inquiries, visits)
├── requirments.txt       ← Python dependencies
├── .env                  ← API keys (GROQ_API_KEY)
├── data/
│   ├── marketplace.db    ← SQLite database
│   └── properties.json   ← Seed data (auto-loaded on first run)
├── frontend/
│   ├── auth.js           ← Shared auth + modals (inlined into every page)
│   ├── landing_page.html ← Homepage
│   ├── listing.html      ← Live property grid with filters
│   ├── zara.html         ← AI chat interface
│   ├── byer_search.html  ← Buyer search + inquiry submission
│   ├── seller_dashboard.html ← Seller CRUD + inquiry view
│   ├── market_trends.html
│   └── about.html
├── tools/
│   ├── property_search.py
│   └── calendar_booking.py
└── memory/
    └── user_memory.py

⚙️  Setup & Run
Step 1 — Get a free Groq API key
Go to https://console.groq.com → sign up → create an API key. It's free with generous limits.

Step 2 — Install dependencies
pip install -r requirments.txt

Step 3 — Add your API key
echo "GROQ_API_KEY=your_key_here" > .env

Step 4 — Start the server
uvicorn server:app --reload --port 8000
You should see:   ✅ Database initialized   |   INFO: Uvicorn running on http://127.0.0.1:8000

Step 5 — Open in browser
http://127.0.0.1:8000
Do NOT open the HTML files directly from your filesystem — always go through the server URL above so that auth.js and inter-page links work correctly.

🗺  Pages & URLs
Page	URL	Description
Homepage	http://127.0.0.1:8000	Landing page
Listings	/app/listing.html	Live property grid + filters
Zara AI Chat	/app/zara.html	Conversational AI search
Buyer Search	/app/byer_search.html	Search + contact seller
Seller Dashboard	/app/seller_dashboard.html	Manage your listings
Market Trends	/app/market_trends.html	Price insights

🔌  API Endpoints
Method	Endpoint	Description
GET	/api/properties	List all available properties (filterable)
POST	/api/properties	Create a new property listing
PUT	/api/properties/{id}	Update property (price, status, etc.)
DELETE	/api/properties/{id}	Delete a property
GET	/api/seller/{phone}/properties	Get all listings by a seller
GET	/api/seller/{phone}/inquiries	Get all buyer inquiries for a seller
POST	/api/inquiries	Submit buyer inquiry to seller
GET	/api/stats	Platform stats (total properties, avg price)
POST	/chat	Send message to Zara AI (REST)
WS	/ws/{session_id}	Real-time Zara AI chat (WebSocket)
GET	/health	Server health + Groq config check

🔐  Authentication
Estate-AI uses phone-number-based authentication — no passwords required. When a user enters their name and phone number, the session is saved in localStorage and shared across all pages. Signing up as a Seller auto-redirects to the Seller Dashboard.

•	Sign In / Sign Up modal appears on every page (top-right button)
•	Session persists across tabs and page refreshes
•	Seller Dashboard auto-logins if you're already signed in on another page
•	'List Property' button on every page — requires sign-in first

🤖  Zara — AI Concierge
Zara is the AI brain of Estate-AI. She speaks Urdu and English, searches the live property database using tool calls, and returns structured results with property cards. She is powered by Groq's LLaMA 3.3-70b model — one of the fastest inference APIs available.

•	Conversational property search: 'DHA mein 10 Marla house chahiye'
•	Budget-aware: '5 Crore mein kya available hai?'
•	Market insights: 'Bahria Town vs DHA — ROI comparison'
•	Voice input via Web Speech API (mic button, Urdu/English)
•	Property cards rendered inline in chat
•	Session memory — remembers preferences within a conversation

🐛  Troubleshooting
•	 — run: pip install -r requirments.txt (note the typo in the filename)ModuleNotFoundError
•	 — make sure uvicorn is running on port 8000Zara says 'Backend not connected'
•	 — open via http://127.0.0.1:8000, NOT by double-clicking the HTML fileButtons not working
•	 — check your .env file: GROQ_API_KEY=sk-... with no quotesGroq API error

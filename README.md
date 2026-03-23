# Anonymous Chat Bot
![Chat Match Bot](pingpong.jpg)

 for anonymous chat with gender and age preferences.
---
## 🔎 How It Works
1. User starts with `/start`.
2. Bot asks for gender → user selects.
3. Bot asks for age → user enters a number between 18–99.
4. Bot asks for preferred partner’s gender → user selects.
5. Bot asks for preferred partner’s age range → user selects.
6. User is added to the waiting queue.
7. Bot searches for a matching partner:
   - Gender preferences must align.
   - Age must fit within both users’ chosen ranges.
8. If a match is found → both users are connected anonymously.
9. Messages are forwarded between users until one ends the chat.
10. Chat can be ended via button **“End Chat”** or `/stop`.
---
## ⚙️ Installation
1. Clone the repository:
git clone https://github.com/username/anon-chat-bot.git
cd anon-chat-bot

2. Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


3. Install dependencies:
pip install -r requirements.txt
4. Create `.env` file in the project root:
TOKEN=your-telegram-bot-token


5. Run locally:
python bot.py
---
## 🐳 Docker
1. Build image:
docker build -t anon-chat-bot .
2. Run container:
docker run -e TOKEN=your-telegram-bot-token anon-chat-bot
3. Detached mode:
docker run -d -e TOKEN=your-telegram-bot-token --name chatbot anon-chat-bot
4. Manage:
docker stop chatbot
docker start chatbot
docker logs chatbot

---

## 📂 Files
- `bot.py` — main bot logic  
- `requirements.txt` — dependencies  
- `Dockerfile` — container setup  
- `README.md` — documentation  
- `LICENSE` — license  
---

## 📖 Usage
- `/start` — begin  
- `/stop` — end chat  
- Inline buttons — choose gender, age, preferences 

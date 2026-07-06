# 🚀 DesignMentor AI - Quick Start Guide

Get started in **under 2 minutes**!

---

## ⚡ Quick Setup

### Step 1: Install Dependencies (30 seconds)
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key (30 seconds)
1. Get free Groq API key: https://console.groq.com/keys
2. Copy `.env.example` to `.env`
3. Add your API key to `.env`:
```env
GROQ_API_KEY=your_key_here
```

### Step 3: Run Server (10 seconds)
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 4: Open Browser
```
http://localhost:8000
```

**Done! 🎉**

---

## 🎯 First Steps

### 1. Generate Your First Design
1. Click the **"Design"** tab
2. Type a system name: `Instagram`
3. Click **"Generate Design"**
4. Wait 10-15 seconds
5. View your complete system design!

### 2. Try a Mock Interview
1. Click the **"Interview"** tab
2. Enter a topic: `Netflix`
3. Click **"Start Interview"**
4. Read the first question
5. Type your answer
6. Click **"Submit Answer"**
7. Review your evaluation score

### 3. Generate a Diagram
1. Click the **"Diagram"** tab
2. Enter system: `Uber`
3. Add summary: `Riders request trips, matched with drivers`
4. Click **"Generate Diagram"**
5. View interactive Mermaid diagram

---

## 🎨 UI Overview

### Six Main Tabs

| Tab | Purpose | Best For |
|-----|---------|----------|
| 🏗️ **Design** | Generate complete system designs | Learning architecture patterns |
| 🎤 **Interview** | Mock interview with AI evaluation | Interview preparation |
| 📊 **Evaluate** | One-shot answer evaluation | Quick feedback |
| 🗺️ **Diagram** | Architecture diagram generation | Visualizing systems |
| 📚 **Feedback** | Learning reports & resources | Improvement tracking |
| 💬 **Chat** | Free-form coaching | Asking questions |

---

## 💡 Pro Tips

### For Best Results

1. **Be Specific**: Instead of "design a social network", say "design Instagram's photo sharing"
2. **Be Detailed**: Provide thorough answers (3-5 sentences minimum)
3. **Think Aloud**: Explain your reasoning and trade-offs
4. **Cover Basics**: Always mention scalability, availability, consistency

### Common Topics to Try

**Easy:**
- URL Shortener
- Pastebin
- Rate Limiter

**Medium:**
- Twitter
- Instagram
- Uber
- Netflix

**Hard:**
- WhatsApp
- YouTube
- Google Search
- Distributed File System

---

## 🔧 Troubleshooting

### Server Won't Start
```bash
# Make sure port 8000 is free
netstat -ano | findstr :8000

# If in use, kill the process or use different port
python -m uvicorn app.main:app --port 8001
```

### Groq API Errors
- **429 Too Many Requests**: Wait 60 seconds (free tier: 30 req/min)
- **401 Unauthorized**: Check your API key in `.env`
- **Connection Error**: Check internet connection

### Slow Responses
- **Normal**: 5-15 seconds for design generation
- **Groq Rate Limit**: Wait 60 seconds
- **Internet Issue**: Check connection speed

---

## 📚 What to Try First

### Beginner Path
1. Generate a design for "URL Shortener"
2. Read through the output
3. Try the Interview tab with same topic
4. Generate a diagram for visual understanding

### Intermediate Path
1. Start interview for "Instagram"
2. Answer 3-5 questions
3. Generate full design for comparison
4. Get feedback report

### Advanced Path
1. Start interview for "WhatsApp"
2. Complete all 5 questions
3. Use Evaluate tab for deeper analysis
4. Use Chat tab to ask follow-up questions

---

## 🎓 Learning Approach

### Week 1: Fundamentals
- Try 5 easy systems (URL shortener, pastebin, etc.)
- Focus on understanding requirements
- Learn capacity estimation

### Week 2: Intermediate
- Try 5 medium systems (Twitter, Instagram, etc.)
- Practice API design
- Understand caching strategies

### Week 3: Advanced
- Try 5 hard systems (YouTube, WhatsApp, etc.)
- Master scaling patterns
- Practice interview responses

### Week 4: Interview Prep
- Do full mock interviews daily
- Time yourself (45 minutes)
- Review feedback reports
- Focus on weak areas

---

## 🚀 Power User Features

### Session Management
- Each tab maintains its own session
- Sessions auto-expire after 30 minutes
- Use Chat tab for continuous learning

### Keyboard Shortcuts
- `Tab`: Navigate between fields
- `Enter`: Submit in single-line inputs
- `Ctrl+Enter`: Submit in textareas

### Export & Share
- Copy generated designs to clipboard
- Save Mermaid diagrams as images
- Share session IDs for feedback

---

## 📞 Need Help?

### Resources
- **Full Docs**: See `README.md`
- **API Reference**: http://localhost:8000/docs
- **Project Status**: See `STATUS.md`
- **Complete Guide**: See `PROJECT_COMPLETE.md`

### Common Questions

**Q: How long do sessions last?**
A: 30 minutes from last activity

**Q: Can I use a different LLM?**
A: Yes! Edit `app/chains.py` to use OpenAI, Anthropic, etc.

**Q: Is my data saved?**
A: Sessions are in-memory only (not persisted to disk)

**Q: How many requests can I make?**
A: Groq free tier: 30 per minute, 14,400 per day

---

## 🎉 You're Ready!

Open **http://localhost:8000** and start mastering system design interviews!

**Happy Learning! 🚀**

---

*Quick Start Guide v1.0*  
*For detailed documentation, see README.md*

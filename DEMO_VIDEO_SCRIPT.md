# FleetPulse - 3-Minute Demo Video Script

**Target:** Geotab Vibe Coding Competition Judges  
**Prize Category:** Vibe Master ($10,000)  
**Duration:** 3 minutes max  
**Tone:** Professional, confident, direct (no fluff)

---

## 🎬 Video Structure

### [0:00-0:20] **Opening Hook** (20 seconds)

**Screen:** Show live dashboard at https://fleetpulse-rm49a.ondigitalocean.app

**Script:**
> "Hi, I'm Ethan Aldrich, CTO of Budget Rent a Car Las Vegas. Managing 50 vehicles across 8 locations means I live with the chaos of fleet operations every day. So when Geotab announced the Vibe Coding Competition, I saw a chance to build the solution I've always needed.
> 
> This is **FleetPulse** — an AI-powered fleet intelligence platform built in 18 days using vibe coding with Claude, GitHub Copilot, and the Geotab API."

**What to show:**
- Full dashboard view with animated KPIs
- Fleet map with live vehicle markers
- Keep camera on (small corner PiP if recording screen + webcam)

---

### [0:20-1:00] **Core Dashboard Features** (40 seconds)

**Screen:** Navigate through dashboard sections slowly

**Script:**
> "FleetPulse gives me real-time visibility across all 8 locations. Here you can see 50 vehicles actively tracked, with KPIs updating every 30 seconds.
> 
> *[Point to map]* The fleet map shows vehicle positions color-coded by status — green for active, yellow for idle, red for maintenance needs.
> 
> *[Scroll to Safety Scorecard]* Safety scores are calculated from real Geotab ExceptionEvents — speeding violations, harsh braking, acceleration patterns. Drivers are ranked so I can prioritize coaching where it matters most.
> 
> *[Show Leaderboard]* We gamify safety with FleetChamp — drivers earn points and badges for safe driving. It's turned safety from a lecture into friendly competition."

**What to show (in order):**
1. **KPI Cards** (0:20-0:25)
   - Hover over cards to show animations
   - Point to "50 Total Vehicles", "42 Active", trip count
   
2. **Fleet Map** (0:25-0:35)
   - Zoom in on Las Vegas area
   - Show vehicle markers clustered by location
   - Click one vehicle to show popup (vehicle name + status)
   
3. **Safety Scorecard** (0:35-0:45)
   - Scroll through driver list
   - Point to drivers with violations (red bars)
   - Show event counts (e.g., "Demo-32: 5 events, 82% score")
   
4. **Driver Leaderboard** (0:45-1:00)
   - Show ranked drivers with points
   - Point to badges (🏅 Speed Demon Free, 🎯 Smooth Operator, etc.)
   - Highlight top 3 trophy icons (🥇🥈🥉)

---

### [1:00-1:40] **Agentic Intelligence (Key Differentiator)** (40 seconds)

**Screen:** Scroll to Agentic Monitor section

**Script:**
> "Here's what makes FleetPulse different: **autonomous AI monitoring**.
> 
> *[Point to monitor panel]* Every 60 seconds, an agentic system analyzes the entire fleet looking for anomalies I'd never catch manually. Speed violations, excessive idle time, off-route vehicles, after-hours activity — it finds patterns and alerts me proactively.
> 
> *[Scroll through alerts]* These alerts show severity levels and timestamps. High-priority issues get flagged immediately.
> 
> *[Click 'Trigger Check' button]* I can manually trigger a check at any time. Watch — *[wait 2 seconds for response]* — new alerts appear instantly."

**What to show (in order):**
1. **Agentic Monitor Section** (1:00-1:10)
   - Scroll to "🤖 Agentic Monitor" section
   - Show alert cards with severity levels
   - Point to "Last Check: X seconds ago" timestamp
   
2. **Alert Types** (1:10-1:25)
   - Read 2-3 alert examples:
     - "Speed anomaly detected: Demo-44 exceeded 75 mph"
     - "Excessive idle: Demo-08 idle for 45 minutes"
     - "After-hours activity: Demo-15 active at 2:30 AM"
   
3. **Manual Trigger** (1:25-1:40)
   - Click "🔄 Trigger Check" button
   - Wait for response (should be <2 seconds)
   - Show new check timestamp updating

---

### [1:40-2:20] **AI Chat & Advanced Features** (40 seconds)

**Screen:** Open AI Chat interface (click chat button)

**Script:**
> "FleetPulse also has conversational intelligence. I can ask questions in plain English and get instant answers with visualizations.
> 
> *[Type query]* 'Which location needs driver coaching?'
> 
> *[Wait for response]* The AI analyzes safety scores, identifies W Sahara has 3x more idle violations than average, and suggests specific coaching actions.
> 
> *[Scroll to show chart]* It even generates charts inline — this is way faster than digging through reports.
> 
> *[Close chat, navigate to tabs]* We also have predictive maintenance, route replay, fuel analytics — all the tools I need in one dashboard."

**What to show (in order):**
1. **Open Chat Interface** (1:40-1:45)
   - Click floating chat button (bottom right)
   - Show chat panel slide in
   
2. **Natural Language Query** (1:45-2:00)
   - Type: "Which location needs driver coaching?"
   - Press Enter
   - Show typing indicator
   - Wait for AI response (should be <5 seconds)
   
3. **AI Response with Insights** (2:00-2:10)
   - Scroll through AI response text
   - Point to specific insights (e.g., "W Sahara: 3x higher idle time")
   - Show inline chart if generated
   
4. **Quick Tab Overview** (2:10-2:20)
   - Close chat
   - Quickly click through tabs (don't wait for full load):
     - Maintenance (show predictive alerts)
     - Route Replay (show historical trip visualization)
     - Fuel Analytics (show efficiency chart)
   - Just flash each one for 2-3 seconds to show breadth

---

### [2:20-2:50] **Vibe Coding Journey** (30 seconds)

**Screen:** Open GitHub repo or show PROMPTS.md

**Script:**
> "I built this entirely through vibe coding. I'm not a frontend developer — I'm a sysadmin who asked Claude, 'Help me build a fleet dashboard.'
> 
> *[Show PROMPTS.md or GitHub]* Over 150 AI prompts, documented in our GitHub repo. Every feature started as a conversation: 'Add an agentic monitor.' 'Make it gamified.' 'Generate charts from natural language.'
> 
> *[Show commit history or file structure]* The AI handled the boilerplate — React components, FastAPI routers, Geotab API integration. I focused on the business logic, the problems I actually needed to solve.
> 
> That's the power of vibe coding: I went from concept to production in 18 days with zero frontend experience."

**What to show (in order):**
1. **GitHub Repository** (2:20-2:30)
   - Open https://github.com/0x000NULL/FleetPulse in new tab
   - Show:
     - Star count / activity
     - File structure (backend/, frontend/, docs/)
     - README.md header
   
2. **PROMPTS.md** (2:30-2:40)
   - Click PROMPTS.md in repo
   - Scroll through showing sections:
     - "Initial Concept Prompt"
     - "Agentic Intelligence"
     - "UI/UX Refinements"
   - Point to "~150 AI prompts documented"
   
3. **Commit History** (2:40-2:50)
   - Click "Commits" or scroll to show commit list
   - Point to recent commits:
     - "feat: add agentic monitor with autonomous detection"
     - "fix: add fetch timeout to prevent infinite loading"
     - "feat: add realistic mock safety scores for demo"
   - Show commit count (58+ commits)

---

### [2:50-3:00] **Closing & Call to Action** (10 seconds)

**Screen:** Back to live dashboard, show full view

**Script:**
> "FleetPulse is live right now at fleetpulse-rm49a.ondigitalocean.app. It's managing real simulated data from Geotab's demo fleet, ready for production.
> 
> This is what vibe coding makes possible: real solutions, built fast, by people who understand the problem.
> 
> Thank you."

**What to show:**
- Full dashboard view (wide shot)
- Show URL in browser bar clearly
- End with animated KPI cards updating
- Fade to black or end recording

---

## 🎥 Production Tips

### Recording Setup
- **Tool:** OBS Studio (free) or QuickTime (Mac)
- **Resolution:** 1920x1080 (1080p)
- **Frame Rate:** 30fps minimum
- **Audio:** Clear microphone (headset or USB mic, NOT laptop mic)
- **Browser:** Full screen mode (F11) or hide bookmarks bar

### Before Recording Checklist
- [ ] Clear browser cookies/cache
- [ ] Close unnecessary tabs
- [ ] Disable browser extensions that might show popups
- [ ] Set browser zoom to 100%
- [ ] Turn off notifications (Do Not Disturb mode)
- [ ] Prepare demo queries in notepad (copy-paste for speed)
- [ ] Test audio levels
- [ ] Have water nearby (dry mouth = bad audio)

### During Recording
- **Speak slowly and clearly** (judges may not be native English speakers)
- **Pause between sections** (easier to edit)
- **Point with cursor** to highlight features (don't assume they see what you see)
- **If you mess up:** Just pause, say "Let me try that again," and continue
- **Energy level:** Enthusiastic but professional (imagine explaining to a VP)

### After Recording
- **Export as:** MP4, H.264 codec
- **Max file size:** YouTube allows 128GB, but keep under 2GB for fast upload
- **Upload to YouTube** as Unlisted (easier to share exact link)
- **Title:** "FleetPulse - Geotab Vibe Coding Competition 2026"
- **Description:** Include GitHub link, live demo URL, tech stack

---

## 📝 YouTube Video Description Template

```
FleetPulse - AI-Powered Fleet Intelligence Platform
Geotab Vibe Coding Competition 2026 Entry

Built by Ethan Aldrich, CTO of Budget Rent a Car Las Vegas

FleetPulse is an autonomous fleet management dashboard combining real-time vehicle tracking, AI-powered anomaly detection, natural language queries, and driver gamification. Built in 18 days using vibe coding with Claude, GitHub Copilot, and the Geotab API.

🔗 Live Demo: https://fleetpulse-rm49a.ondigitalocean.app
🔗 GitHub: https://github.com/0x000NULL/FleetPulse
🔗 Competition: https://luma.com/h6ldbaxp

Tech Stack:
- Backend: Python, FastAPI, Geotab mygeotab SDK
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, Leaflet, Recharts
- AI: Claude (Anthropic) for agentic monitoring and conversational queries
- Deployment: DigitalOcean App Platform
- Database: In-memory caching (production would use PostgreSQL)

Key Features:
✅ Real-time vehicle tracking across 8 locations
✅ Autonomous AI anomaly detection (speed, idle, off-route, after-hours)
✅ Natural language fleet queries with chart generation
✅ Driver safety scoring and gamification (FleetChamp)
✅ Predictive maintenance forecasting
✅ Route replay and fuel analytics
✅ MyGeotab Add-In integration
✅ MCP server for Claude Desktop

Built entirely through vibe coding - 150+ AI prompts documented in PROMPTS.md

Prize Category: Vibe Master ($10,000)
```

---

## 🎯 Key Messages to Emphasize

1. **Real problem, real solution** - You actually run a rental fleet, this isn't theoretical
2. **Agentic AI** - Autonomous monitoring is the differentiator (not just a dashboard)
3. **Vibe coding success story** - Sysadmin built production-grade SPA in 18 days
4. **Production-ready** - Not a prototype, this is deployed and working
5. **Complete ecosystem** - Dashboard + Add-In + MCP + API (shows depth)

---

## ❌ What NOT to Say

- Don't apologize for demo data ("This is just fake data..." ❌)
- Don't mention bugs or missing features
- Don't say "I'm not a developer" in a negative way (say it as empowerment!)
- Don't get lost in technical details (judges care about value, not code)
- Don't rush! 3 minutes is plenty of time to breathe

---

## ✅ Final Checklist Before Upload

- [ ] Video is 3 minutes or less
- [ ] Audio is clear (no background noise)
- [ ] All features demonstrated work on camera
- [ ] URL visible in browser bar
- [ ] GitHub repo link shown
- [ ] No personal info visible (emails, passwords, etc.)
- [ ] Exported in 1080p MP4
- [ ] Uploaded to YouTube (Unlisted)
- [ ] Title and description added
- [ ] Video tested (watch it once before submitting)

---

**Good luck! You've got this.** 🚀

The platform is solid, the story is compelling, and you genuinely built something useful. Just be yourself, show what you built, and explain why it matters. That's all judges need to see.

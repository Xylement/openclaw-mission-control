from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime
import random

app = FastAPI(title="Mission Control")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Mission Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #1e1e2e; margin-bottom: 30px; }
        h1 { font-size: 1.8rem; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #12121a; border: 1px solid #1e1e2e; border-radius: 12px; padding: 20px; }
        .stat-card h3 { color: #888; font-size: 0.85rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .stat-card .value { font-size: 2rem; font-weight: 700; }
        .stat-card .value.cyan { color: #00d4ff; }
        .stat-card .value.purple { color: #7c3aed; }
        .stat-card .value.green { color: #10b981; }
        .stat-card .value.orange { color: #f59e0b; }
        .section { background: #12121a; border: 1px solid #1e1e2e; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .section h2 { font-size: 1.1rem; margin-bottom: 15px; color: #fff; }
        .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .agent-card { background: #0a0a0f; border: 1px solid #1e1e2e; border-radius: 8px; padding: 15px; }
        .agent-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .agent-name { font-weight: 600; }
        .agent-status { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; }
        .agent-status.online { background: #10b98122; color: #10b981; }
        .agent-status.busy { background: #f59e0b22; color: #f59e0b; }
        .agent-status.offline { background: #ef444422; color: #ef4444; }
        .activity-list { max-height: 400px; overflow-y: auto; }
        .activity-item { display: flex; gap: 15px; padding: 12px 0; border-bottom: 1px solid #1e1e2e; }
        .activity-item:last-child { border: none; }
        .activity-time { color: #666; font-size: 0.8rem; min-width: 60px; }
        .activity-text { color: #aaa; }
        .login-screen { display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .login-box { background: #12121a; border: 1px solid #1e1e2e; border-radius: 12px; padding: 40px; width: 100%; max-width: 400px; }
        .login-box h2 { text-align: center; margin-bottom: 30px; }
        .login-box input { width: 100%; padding: 12px; background: #0a0a0f; border: 1px solid #1e1e2e; border-radius: 8px; color: #fff; margin-bottom: 15px; font-size: 1rem; }
        .login-box button { width: 100%; padding: 12px; background: linear-gradient(90deg, #00d4ff, #7c3aed); border: none; border-radius: 8px; color: #fff; font-size: 1rem; cursor: pointer; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div id="login-screen" class="login-screen">
        <div class="login-box">
            <h2>🔐 Mission Control</h2>
            <input type="password" id="token-input" placeholder="Enter your auth token">
            <button onclick="login()">Access Dashboard</button>
        </div>
    </div>
    <div id="dashboard" class="container hidden">
        <header>
            <h1>🚀 OpenClaw Mission Control</h1>
            <div>
                <span style="color: #666;">Welcome, Admin</span>
                <button onclick="logout()" style="margin-left: 15px; padding: 8px 16px; background: #1e1e2e; border: none; border-radius: 6px; color: #fff; cursor: pointer;">Logout</button>
            </div>
        </header>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Active Agents</h3>
                <div class="value cyan" id="active-agents">12</div>
            </div>
            <div class="stat-card">
                <h3>Tasks Today</h3>
                <div class="value purple" id="tasks-today">847</div>
            </div>
            <div class="stat-card">
                <h3>Cost Today</h3>
                <div class="value green" id="cost-today">$12.45</div>
            </div>
            <div class="stat-card">
                <h3>Uptime</h3>
                <div class="value orange" id="uptime">99.9%</div>
            </div>
        </div>
        <div class="section">
            <h2>🤖 Active Agents</h2>
            <div class="agents-grid" id="agents-list"></div>
        </div>
        <div class="section">
            <h2>📡 Live Activity</h2>
            <div class="activity-list" id="activity-list"></div>
        </div>
    </div>
    <script>
        const TOKEN = localStorage.getItem('mc_token') || '';
        
        function login() {
            const input = document.getElementById('token-input').value;
            if(input) {
                localStorage.setItem('mc_token', input);
                location.reload();
            }
        }
        
        function logout() {
            localStorage.removeItem('mc_token');
            location.reload();
        }
        
        if(TOKEN) {
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
            loadData();
            setInterval(loadData, 5000);
        }
        
        async function loadData() {
            try {
                const headers = { 'Authorization': 'Bearer ' + TOKEN };
                const [agentsRes, activityRes, statsRes] = await Promise.all([
                    fetch('/api/agents', { headers }),
                    fetch('/api/activity', { headers }),
                    fetch('/api/stats', { headers })
                ]);
                
                if(agentsRes.ok) {
                    const agents = await agentsRes.json();
                    renderAgents(agents);
                }
                if(activityRes.ok) {
                    const activity = await activityRes.json();
                    renderActivity(activity);
                }
                if(statsRes.ok) {
                    const stats = await statsRes.json();
                    document.getElementById('active-agents').textContent = stats.active_agents;
                    document.getElementById('tasks-today').textContent = stats.tasks_today;
                    document.getElementById('cost-today').textContent = stats.cost_today;
                    document.getElementById('uptime').textContent = stats.uptime;
                }
            } catch(e) { console.log('Using mock data'); renderMockData(); }
        }
        
        function renderAgents(agents) {
            const html = agents.map(a => `
                <div class="agent-card">
                    <div class="agent-header">
                        <span class="agent-name">${a.name}</span>
                        <span class="agent-status ${a.status}">${a.status}</span>
                    </div>
                    <div style="color: #666; font-size: 0.85rem;">
                        <div>Tasks: ${a.tasks}</div>
                        <div>Cost: ${a.cost}</div>
                    </div>
                </div>
            `).join('');
            document.getElementById('agents-list').innerHTML = html || '<p style="color:#666">No active agents</p>';
        }
        
        function renderActivity(activity) {
            const html = activity.map(a => `
                <div class="activity-item">
                    <span class="activity-time">${a.time}</span>
                    <span class="activity-text">${a.message}</span>
                </div>
            `).join('');
            document.getElementById('activity-list').innerHTML = html || '<p style="color:#666">No recent activity</p>';
        }
        
        function renderMockData() {
            renderAgents([
                { name: 'scout-01', status: 'online', tasks: 234, cost: '$3.21' },
                { name: 'worker-alpha', status: 'busy', tasks: 89, cost: '$4.56' },
                { name: 'data-collector', status: 'online', tasks: 156, cost: '$2.34' },
                { name: 'monitor-bot', status: 'online', tasks: 45, cost: '$0.89' }
            ]);
            renderActivity([
                { time: '2m ago', message: 'Task completed: data_collection_2024' },
                { time: '5m ago', message: 'Agent scout-01 started' },
                { time: '8m ago', message: 'Cost threshold alert cleared' },
                { time: '12m ago', message: 'New task assigned to worker-alpha' }
            ]);
        }
    </script>
</body>
</html>
"""

# Mock data for demo
MOCK_AGENTS = [
    {"name": "scout-01", "status": "online", "tasks": 234, "cost": "$3.21"},
    {"name": "worker-alpha", "status": "busy", "tasks": 89, "cost": "$4.56"},
    {"name": "data-collector", "status": "online", "tasks": 156, "cost": "$2.34"},
    {"name": "monitor-bot", "status": "online", "tasks": 45, "cost": "$0.89"},
    {"name": "task-runner-1", "status": "busy", "tasks": 312, "cost": "$5.67"},
    {"name": "api-gateway", "status": "online", "tasks": 78, "cost": "$1.23"}
]

MOCK_ACTIVITY = [
    {"time": "2m ago", "message": "Task completed: data_collection_2024"},
    {"time": "5m ago", "message": "Agent scout-01 started"},
    {"time": "8m ago", "message": "Cost threshold alert cleared"},
    {"time": "12m", "12 "ago", "message": "New task assigned to worker-alpha"},
    {"time": "15m ago", "message": "Database connection established"},
    {"time": "18m ago", "message": "Health check passed"}
]

def verify_token(authorization: str = Header(None)):
    token = os.getenv("LOCAL_AUTH_TOKEN", "a/+hYrFxU7vFaay5ge59C13JZS7qD5pO7X7SDC9USV3dAhsaCmInSg1oroSmwSPHYCQ=")
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    if authorization.replace("Bearer ", "") != token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

@app.get("/", response_class=HTMLResponse)
async def root():
    return DASHBOARD_HTML

@app.get("/api/agents")
async def get_agents(authorization: str = Header(None)):
    try:
        verify_token(authorization)
    except:
        return MOCK_AGENTS
    return MOCK_AGENTS

@app.get("/api/activity")
async def get_activity(authorization: str = Header(None)):
    try:
        verify_token(authorization)
    except:
        return MOCK_ACTIVITY
    return MOCK_ACTIVITY

@app.get("/api/stats")
async def get_stats(authorization: str = Header(None)):
    try:
        verify_token(authorization)
    except:
        return {
            "active_agents": 12,
            "tasks_today": 847,
            "cost_today": "$12.45",
            "uptime": "99.9%"
        }
    return {
        "active_agents": 12,
        "tasks_today": 847,
        "cost_today": "$12.45",
        "uptime": "99.9%"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

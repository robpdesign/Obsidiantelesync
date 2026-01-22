# 📱 Telegram to Obsidian Quick Capture

Capture fleeting thoughts on mobile via Telegram, automatically synced to your Obsidian vault.

![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-F38020?logo=cloudflare&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **Quick Capture** – Text thoughts to your Telegram bot like messaging a friend
- **Cloud Queuing** – Messages stored securely until your PC syncs them
- **Auto-Sync** – Pulls thoughts automatically when your computer starts
- **Organized Output** – Thoughts grouped by date with timestamps
- **Private & Secure** – Bot only responds to your Telegram account
- **Free Hosting** – Runs on Cloudflare's generous free tier

## 📖 How It Works

```
┌──────────────┐     ┌───────────────────┐     ┌─────────────────┐
│   You on     │────▶│  Cloudflare       │────▶│  Cloudflare KV  │
│   Telegram   │     │  Worker           │     │  (Storage)      │
└──────────────┘     └───────────────────┘     └────────┬────────┘
                                                        │
                                                        ▼
┌──────────────┐     ┌───────────────────┐     ┌─────────────────┐
│   Obsidian   │◀────│  Local Sync       │◀────│  When PC is on  │
│   Vault      │     │  Script           │     │                 │
└──────────────┘     └───────────────────┘     └─────────────────┘
```

1. **You** send a thought to your Telegram bot while on the go
2. **Cloudflare Worker** receives it, timestamps it, stores it in KV
3. **Local sync script** runs when your PC starts, pulls new thoughts
4. **Quick Thoughts.md** in your vault gets updated with your captured ideas

## 📋 Prerequisites

- [Cloudflare account](https://dash.cloudflare.com/sign-up) (free)
- [Telegram account](https://telegram.org/)
- [Python 3.8+](https://python.org) installed on your PC
- An Obsidian vault

## 🚀 Quick Start

### 1. Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Save the **bot token** (looks like `123456789:ABCdefGHI...`)

### 2. Get Your Telegram User ID

1. Search for **@userinfobot** in Telegram
2. Send it any message
3. Save the **user ID** it returns

### 3. Set Up Cloudflare

#### Create KV Namespace

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **Storage and Databases** → **KV**
3. Click **Create namespace**
4. Name it `obsidian-thoughts`
5. Copy the **Namespace ID**

#### Deploy the Worker

1. Go to **Workers & Pages** → **Create** → **Create Worker**
2. Name it `obsidian-quick-thoughts`
3. Click **Deploy**
4. Click **Edit code**
5. Replace the code with the contents of [`cloudflare-worker/worker.js`](cloudflare-worker/worker.js)
6. **Important:** Update these lines at the top with your values:
   ```javascript
   const TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';
   const ALLOWED_USER_ID = YOUR_USER_ID_HERE;
   ```
7. Click **Save and Deploy**

#### Bind KV Storage

1. Go to your worker → **Settings** → **Variables and Secrets**
2. Find **KV Namespace Bindings** → **Add**
3. Variable name: `THOUGHTS_KV`
4. Select your `obsidian-thoughts` namespace
5. Save

#### Initialize the Webhook

1. Visit: `https://obsidian-quick-thoughts.YOUR_SUBDOMAIN.workers.dev/setup-webhook`
2. Save the `syncSecret` from the response – you'll need it!

### 4. Test Your Bot

1. Open your bot in Telegram
2. Send `/start`
3. You should see: "✅ Connected!"
4. Send a test thought
5. You should see: "💭 Captured!"

### 5. Configure Local Sync

1. Install the requests library:
   ```bash
   pip install requests
   ```

2. Download [`local-sync/sync_thoughts.py`](local-sync/sync_thoughts.py)

3. Edit the configuration at the top:
   ```python
   WORKER_URL = "https://obsidian-quick-thoughts.YOUR_SUBDOMAIN.workers.dev"
   SYNC_SECRET = "your-sync-secret-from-step-3"
   VAULT_PATH = Path(r"C:\path\to\your\vault\Daily Notes")
   ```

4. Test it:
   ```bash
   python sync_thoughts.py
   ```

### 6. Auto-Run on Windows Startup

1. Save [`local-sync/run_sync.bat`](local-sync/run_sync.bat) alongside your Python script
2. Press `Win + R`, type `shell:startup`, press Enter
3. Create a shortcut to `run_sync.bat` in this folder

Now your thoughts sync automatically whenever you log in!

## 📁 Project Structure

```
telegram-obsidian-sync/
├── cloudflare-worker/
│   └── worker.js          # Cloudflare Worker code
├── local-sync/
│   ├── sync_thoughts.py   # Python sync script
│   └── run_sync.bat       # Windows startup script
├── README.md
├── LICENSE
└── .gitignore
```

## 💬 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot |
| `/status` | Check pending thoughts count |
| Any text | Captured as a thought |

## 📝 Output Format

Your `Quick Thoughts.md` will look like:

```markdown
## 2026-01-22
- 09:15 – idea about client presentation
- 14:32 – remember to check that cycling route
- 18:45 – book recommendation from podcast

## 2026-01-21
- 12:30 – thought from yesterday
```

## 🔒 Security

- **User-locked**: Bot only responds to your Telegram user ID
- **Token-protected**: Sync endpoint requires secret bearer token
- **Your data**: Stored in your own Cloudflare account
- **Auto-cleanup**: Thoughts deleted from cloud after successful sync

## 🛠️ Troubleshooting

### Bot not responding?

- Verify your bot token in the worker code
- Re-run the webhook setup: visit `/setup-webhook`
- Check Cloudflare Worker logs for errors

### Sync not working?

- Verify `WORKER_URL` and `SYNC_SECRET` in the Python script
- Ensure KV binding is correctly configured
- Test manually: `python sync_thoughts.py`

### Thoughts not appearing in vault?

- Check `VAULT_PATH` points to the correct folder
- Verify file permissions on the vault folder

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Obsidian](https://obsidian.md) – The incredible knowledge management app
- [Cloudflare Workers](https://workers.cloudflare.com) – Free serverless platform
- [Telegram Bot API](https://core.telegram.org/bots/api) – Simple and powerful

---

**Made with ❤️ for the Obsidian community**

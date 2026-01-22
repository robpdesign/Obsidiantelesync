// Telegram to Obsidian Quick Capture - Cloudflare Worker
// https://github.com/YOUR_USERNAME/telegram-obsidian-sync

// ============ CONFIGURATION ============
// Replace these with your own values
const TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';
const ALLOWED_USER_ID = 0; // Your Telegram user ID (number)
// =======================================

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === '/') {
      return new Response('🧠 Obsidian Quick Thoughts Bot is running', { status: 200 });
    }

    // Telegram webhook endpoint
    if (url.pathname === '/webhook' && request.method === 'POST') {
      return handleTelegramWebhook(request, env);
    }

    // Sync endpoint - local script fetches messages here
    if (url.pathname === '/sync') {
      return handleSync(request, env);
    }

    // Setup webhook endpoint (call once to register)
    if (url.pathname === '/setup-webhook') {
      return setupWebhook(request, env);
    }

    return new Response('Not found', { status: 404 });
  }
};

async function handleTelegramWebhook(request, env) {
  try {
    const update = await request.json();
    
    // Only process messages
    if (!update.message || !update.message.text) {
      return new Response('OK', { status: 200 });
    }

    const message = update.message;
    const userId = message.from.id;
    const text = message.text;
    const chatId = message.chat.id;

    // Security: Only allow messages from your user ID
    if (userId !== ALLOWED_USER_ID) {
      await sendTelegramMessage(chatId, '⛔ Unauthorized. This bot is private.');
      return new Response('OK', { status: 200 });
    }

    // Handle /start command
    if (text === '/start') {
      await sendTelegramMessage(chatId, '✅ Connected! Send me any thought and it will sync to your Obsidian vault.\n\nCommands:\n/status - Check pending thoughts');
      return new Response('OK', { status: 200 });
    }

    // Handle /status command
    if (text === '/status') {
      const pending = await getPendingCount(env);
      await sendTelegramMessage(chatId, `📊 You have ${pending} thought(s) waiting to sync.`);
      return new Response('OK', { status: 200 });
    }

    // Store the thought
    const timestamp = new Date().toISOString();
    const thoughtId = `thought_${Date.now()}`;
    
    await env.THOUGHTS_KV.put(thoughtId, JSON.stringify({
      text: text,
      timestamp: timestamp
    }));

    await sendTelegramMessage(chatId, '💭 Captured!');
    return new Response('OK', { status: 200 });

  } catch (error) {
    console.error('Webhook error:', error);
    return new Response('Error', { status: 500 });
  }
}

async function handleSync(request, env) {
  // Verify sync secret
  const authHeader = request.headers.get('Authorization');
  const expectedSecret = await env.THOUGHTS_KV.get('SYNC_SECRET');
  
  if (!authHeader || authHeader !== `Bearer ${expectedSecret}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    // Get all thoughts
    const list = await env.THOUGHTS_KV.list({ prefix: 'thought_' });
    const thoughts = [];

    for (const key of list.keys) {
      const value = await env.THOUGHTS_KV.get(key.name);
      if (value) {
        thoughts.push({
          id: key.name,
          ...JSON.parse(value)
        });
      }
    }

    // Sort by timestamp
    thoughts.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    // If this is a DELETE request, clear the synced thoughts
    if (request.method === 'DELETE') {
      for (const thought of thoughts) {
        await env.THOUGHTS_KV.delete(thought.id);
      }
      return new Response(JSON.stringify({ cleared: thoughts.length }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // GET request - return thoughts
    return new Response(JSON.stringify({ thoughts }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Sync error:', error);
    return new Response('Error', { status: 500 });
  }
}

async function setupWebhook(request, env) {
  const url = new URL(request.url);
  const workerUrl = `${url.protocol}//${url.host}/webhook`;
  
  const telegramUrl = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${encodeURIComponent(workerUrl)}`;
  
  const response = await fetch(telegramUrl);
  const result = await response.json();
  
  // Also set up the sync secret if not exists
  let syncSecret = await env.THOUGHTS_KV.get('SYNC_SECRET');
  if (!syncSecret) {
    syncSecret = 'obsidian-sync-' + crypto.randomUUID();
    await env.THOUGHTS_KV.put('SYNC_SECRET', syncSecret);
  }
  
  return new Response(JSON.stringify({
    webhook: result,
    syncSecret: syncSecret,
    message: 'Save this sync secret for your local script!'
  }, null, 2), {
    headers: { 'Content-Type': 'application/json' }
  });
}

async function sendTelegramMessage(chatId, text) {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: text
    })
  });
}

async function getPendingCount(env) {
  const list = await env.THOUGHTS_KV.list({ prefix: 'thought_' });
  return list.keys.length;
}

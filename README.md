# ChotiParchi — Voice2Rx on WhatsApp

🏆 1st Place, Ekathon 2025 (Eka.Care × AWS Hackathon)

A WhatsApp bot that turns a doctor's voice note into a structured prescription. A
doctor sends a voice message describing a consultation; the service downloads it,
sends it to Eka Care's AI (Ekascribe) to generate a prescription, and delivers the
formatted result back to the same WhatsApp chat — no manual typing or data entry.

## How it works

```
Doctor sends voice note on WhatsApp
        │
        ▼
Interakt webhook → POST /webhook/whatsapp
        │  (downloads the audio, forwards it to Eka Care)
        ▼
Eka Care AI transcribes + generates the prescription (async)
        │
        ▼
Eka Care webhook → POST /webhook/prescription
        │  (looks up which chat requested it, formats the message)
        ▼
Interakt sends the prescription back on WhatsApp
```

The two webhook endpoints are decoupled because prescription generation is
asynchronous: the first call kicks off the job and returns immediately; Eka Care
calls back on the second endpoint once the prescription is ready. A `request_id`
returned by Eka Care is used to match the callback back to the WhatsApp chat that
asked for it.

## Tech stack

- **FastAPI** — webhook endpoints and request validation (Pydantic models)
- **Eka Care API** — voice-to-prescription AI (Ekascribe)
- **Interakt** — WhatsApp Business API provider (receiving/sending messages)
- **httpx** — async HTTP client for both integrations

## Prerequisites

- Python 3.8+
- Eka Care API credentials (Client ID and Client Secret)
- An Interakt account and API key, with a WhatsApp Business number connected
- A publicly reachable URL for the two webhook endpoints (e.g. via a reverse proxy
  or a tunnel like ngrok during local development)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/init-kaushal/echo-health.git
   cd echo-health
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

## Running the service

```bash
python -m app.main
```

Then register the two webhook URLs against your public URL:
- Interakt → WhatsApp webhook: `https://your-domain.com/webhook/whatsapp`
- Eka Care → prescription callback: `https://your-domain.com/webhook/prescription`

## API endpoints

| Endpoint | Purpose |
|---|---|
| `POST /webhook/whatsapp` | Receives an incoming WhatsApp voice message from Interakt and kicks off prescription generation |
| `POST /webhook/prescription` | Receives the generated prescription from Eka Care and sends it back via WhatsApp |
| `GET /health` | Basic healthcheck |

## Known limitations

This was built for a hackathon (Ekathon 2025) and is shared here as a portfolio
reference rather than a production-ready service. Notably:

- **Webhook endpoints aren't authenticated.** Neither Interakt's nor Eka Care's
  signature/verification scheme is checked, so anyone who discovers the URLs
  could POST arbitrary payloads. Add signature verification before deploying
  this for real use.
- **In-memory request store.** `phone_number_store` (matching a prescription
  request back to the WhatsApp chat that asked for it) is a plain in-process
  dict — it's lost on restart and won't work across multiple instances. Swap
  in a real database (Redis, Postgres, etc.) for production use.
- No rate limiting, retry handling, or structured logging.

## License

[MIT](LICENSE)

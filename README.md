# WhatsApp Voice to Prescription Service

This service integrates WhatsApp (via Interakt) with Eka Care's API to convert voice messages into prescriptions. When a user sends a voice message through WhatsApp, the service processes it and generates a prescription using Eka Care's AI service, then sends the prescription back to the user via WhatsApp.

## Features

- Receives voice messages from WhatsApp via Interakt webhooks
- Processes voice messages and sends them to Eka Care's AI service
- Generates prescriptions using Eka Care's API
- Sends generated prescriptions back to users via WhatsApp

## Prerequisites

- Python 3.8 or higher
- Eka Care API credentials (Client ID and Client Secret)
- Interakt API credentials
- A publicly accessible URL for webhook endpoints
- Webhooks registered in Eka Care backend

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
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

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials:
   ```
   EKA_CLIENT_ID=your_eka_client_id
   EKA_CLIENT_SECRET=your_eka_client_secret
   INTERAKT_API_KEY=your_interakt_api_key
   ```

## Running the Service

1. Start the service:
   ```bash
   python -m app.main
   ```

2. Ensure your webhooks are properly registered:
   - Register the WhatsApp webhook URL in Interakt: `https://your-domain.com/webhook/whatsapp`
   - Register the prescription callback URL in Eka Care backend: `https://your-domain.com/webhook/prescription`

## Usage

1. Users send voice messages to your WhatsApp business number
2. The service receives the voice message via Interakt webhook
3. The voice message is processed and sent to Eka Care's AI service
4. When the prescription is generated, Eka Care sends it back via webhook
5. The service formats the prescription and sends it back to the user via WhatsApp

## API Endpoints

- `POST /webhook/whatsapp`: Receives incoming WhatsApp voice messages
- `POST /webhook/prescription`: Receives prescription generation callbacks from Eka Care

## Security Considerations

- Keep your `.env` file secure and never commit it to version control
- Use HTTPS for all webhook endpoints
- Implement proper authentication for your webhooks in production
- Store request IDs and phone numbers in a proper database for production use

## Error Handling

The service includes basic error handling for:
- Invalid webhook payloads
- Failed voice message downloads
- Failed prescription generation
- Missing request IDs in callbacks
- API authentication issues

## Production Considerations

For production deployment:
1. Use a proper database instead of in-memory storage
2. Implement request validation and rate limiting
3. Add logging and monitoring
4. Use a production-grade ASGI server
5. Set up SSL/TLS certificates
6. Implement proper security measures

## License

[Your chosen license] 
# EkaHealth Voice Assistant

A voice-enabled health assessment system using Eka Care's APIs.

## Features

- Voice-enabled health assessment
- Speech-to-text and text-to-speech functionality
- Real-time feedback
- Integration with Eka Care APIs
- Modern, accessible UI using Material-UI

## Tech Stack

- Frontend:
  - React 18
  - TypeScript
  - Material-UI (MUI)
  - react-speech-kit for voice interactions
  - axios for API calls

- Backend:
  - FastAPI
  - Python
  - Integration with Eka Care APIs

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   cd ../backend
   pip install -r requirements.txt
   ```

3. Start the development servers:
   ```bash
   # Frontend (in frontend directory)
   npm start

   # Backend (in backend directory)
   uvicorn main:app --reload
   ```

4. Open http://localhost:3000 in your browser

## Requirements

- Node.js 16+
- Python 3.8+
- Modern web browser with speech recognition support (Chrome recommended)

## Development Notes

- The application uses Material-UI for the user interface
- Voice interactions are handled through the Web Speech API
- Backend API runs on http://localhost:8000
- Frontend development server runs on http://localhost:3000

## Project Structure

```
echo-health/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application file
│   └── requirements.txt  # Python dependencies
└── frontend/            # React frontend
    ├── src/             # Source code
    ├── public/          # Static files
    └── package.json     # Node.js dependencies
```

## Local Development Setup

### Backend Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The app will be available at http://localhost:3000

## Production Deployment Considerations

### Backend

1. Update CORS settings in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-production-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Set up environment variables:
```bash
# .env
EKA_API_KEY=your_api_key
PRODUCTION=true
```

3. Use a production ASGI server:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

1. Update API endpoint in production:
```javascript
// Create .env.production
REACT_APP_API_URL=https://api.your-production-domain.com
```

2. Build the production bundle:
```bash
npm run build
```

### Security Considerations

1. Enable HTTPS
2. Implement rate limiting
3. Set up proper authentication
4. Store sensitive data in environment variables
5. Use secure session management

## API Integration

To integrate with Eka Care APIs:

1. Sign up for API access at developer.eka.care
2. Add your API keys to environment variables
3. Update the backend endpoints to use actual Eka Care API calls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 
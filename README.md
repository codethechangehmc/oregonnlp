# oregonnlp

## Development Setup

First, clone this repo using

```
git clone https://github.com/codethechangehmc/oregonnlp.git
```

Then start the frontend by running

```
cd frontend
npm install
npm run dev
```

Start the backend by running

```
cd backend
uvicorn app.main:app --reload
```

The app should be properly running on http://localhost:3000 with the backend on http://127.0.0.1:8000

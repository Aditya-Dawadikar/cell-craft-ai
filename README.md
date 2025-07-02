![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/frontend/src/assets/logo.svg)

# CellCraft-AI

**CellCraft-AI** is an intelligent, version-controlled data cleaning assistant built for structured CSV files. It combines large language models (LLMs), commit-based checkpoints, and cloud-native architecture to help users transform, explore, and branch CSV data with traceability and reproducibility.

---

## 🚀 Features

- 💬 **Natural language queries**: Users can request transformations or analysis using plain English.
- 🤖 **LLM-powered transformation engine**: Utilizes Gemini to generate Pandas/Numpy/Matplotlib code.
- ☁️ **Cloud-first architecture**: Files are stored in **AWS S3**, metadata in **MongoDB Atlas**, and URLs are cached using **Redis**.
- 🌲 **Commit history DAG**: Visualize transformation lineage and branch from any prior state.
- 🔁 **Commit-based versioning**: Every data transformation is saved as a separate commit.

---

## 🧱 Architecture

![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/cellcraft-ai-architecture.png)

- **Frontend**: React + Vite
- **Backend**: FastAPI (Python 3.10+)
- **Vector Model**: Gemini-2.5 via Google API
- **Storage**: 
  - File storage → **AWS S3**
  - Metadata → **MongoDB Atlas**

---

## 📦 Setup (Local Dev)

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/cellcraft-ai.git
cd cellcraft-ai
```

### 2. Create ```.env```

#### Backend

```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-west-2
S3_BUCKET_NAME=your-s3-bucket
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/cellcraft-ai
GEMINI_API_KEY=your-google-api-key
```

#### Frontend

```bash
VITE_BASE_URL=http://localhost:8000
```

### 3. Install Dependencies

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm i
```

---
### 3. Run

#### Backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```
npm run dev
```

---

### S3 Setup

CellCraft-AI stores all the AI generated files in 3 formats -- Markdown, CSV and PNG. These files are uploaded to a private S3 bucket. Use the following CORS setup for the bucket.

```bash
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": [
      "http://localhost:8000",
      "http://localhost:5173"
    ],
    "ExposeHeaders": ["ETag", "x-amz-meta-custom-header"],
    "MaxAgeSeconds": 3000
  }
]
```

### MongoDB Setup
[TBD]

---

![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/frontend/src/assets/logo.svg)

# CellCraft-AI

**CellCraft-AI** is an intelligent, version-controlled data cleaning assistant built for structured CSV files. It combines large language models (LLMs), commit-based checkpoints, and cloud-native architecture to help users transform, explore, and branch CSV data with traceability and reproducibility.

---

## Features

- 💬 **Natural language queries**: Users can request transformations or analysis using plain English.
- 🤖 **LLM-powered transformation engine**: Utilizes Gemini to generate Pandas/Numpy/Matplotlib code.
- ☁️ **Cloud-first architecture**: Files are stored in **AWS S3**, metadata in **MongoDB Atlas**, and URLs are cached using **Redis**.
- 🌲 **Commit history DAG**: Visualize transformation lineage and branch from any prior state.
- 🔁 **Commit-based versioning**: Every data transformation is saved as a separate commit.

---

## Architecture

![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/cellcraft-ai-architecture.png)

- **Frontend**: React + Vite
- **Backend**: FastAPI (Python 3.10+)
- **Agent**: Langchain + Gemini-2.5 Flash
- **Storage**: 
  - File storage → **AWS S3**
  - Metadata → **MongoDB Atlas**
  - Cache → **Redis**

---

### Context Management

CellCraftAI uses a [Checkpoint Based Context Management Algorithm](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/docs/docs/ContextCondensation.md)

![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/docs/docs/CheckpointBasedCondensation.png)

---

## CellCraft-AI in Action

![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/CellCraftAI-Demo.gif)

---

## Views
### Dashboard
![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/dashboard.png)

The Dashboard has 4 Panels
- Navigation: Navigate to any previous chats, or create a new project
- Chat: Interact with the agent using simple prompts
- Data Preview: View and Download the data generated
- Commit History: Track data transforms and factual conversations

### Step 1: Start a Project
![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/create-project.png)

Upload a CSV file that you wish to analyse. Each project starts with uploading a CSV. All the conversations will be based on the uploaded CSV. Transformations applied by the Agent will be applied to the same data.

### Step 2: Give a Prompt
![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/Chat.png)

CellCraft's AI is designed to limit its responses to the CSV data, exploration strategies and Analysis reports.
The Agent has access to following libraries in its Sandbox environment
- Numpy
- Pandas
- Matplotlib
- Seaborn

Any instruction to perform task that go beyond the scope of these libraries will result into error reponse.
CellCraft-AI can suggest you what visualizations can be derived from the given data, and do it for you with one prompt.

### Step 3: View Agent's Response
![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/DataOutput.png)

The Agent generates its own code based on the prompt request, executes it in an isolated environment. The programs outputs in the form of Markdown/ CSV/ PNG files which are uploaded to an S3 bucket, and each transform is checkpointed using Git Style Commits, except the commits are internally managed by the Agent. You can also create new branches or change the Commit HEAD to apply new data transforms. At any point you can view the previously generated responses and download the generated files.

### Step 4: Track Transforms
![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/master/docs/Commit-DAG.png)

To make things easier to track, we have provided a Commit tracker UI, its draggable, scrollable, pannable which you can use to view the progression of your data transforms.

---

## Setup (Local Dev)

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
REDIS_URL=redis://localhost:6379
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

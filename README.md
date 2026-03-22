# nodeApp (n8n) Personal Automation Hub

This directory contains the configuration and workflows for a locally-hosted [n8n](https://n8n.io/) instance running via Docker, specifically tailored to automate personal tasks like transcribing and organizing voice memos into Notion.

## Project Structure

- `docker-compose.yml`: The Docker Compose configuration that pulls the official `n8n` image, sets up the persistent volumes (`n8n_data`), and configures essential environment variables (including the ngrok webhook URL).
- `VoiceMemoWorkflow.json`: An exported n8n workflow template. It listens for incoming audio from an iOS Shortcut, transcribes it via OpenAI Whisper, extracts structured data using GPT-4o, and inserts it as a new organized entry in a Notion database.

## 🚀 Getting Started

### 1. Start the n8n Server
Ensure Docker Desktop is running, then open a terminal in this directory and run:
```bash
docker compose up -d
```
This will pull the latest image if necessary and start n8n in the background. You can access the UI at **[http://localhost:5678](http://localhost:5678)**.

### 2. Configure Your Network (ngrok)
To allow external services (like your iPhone on cellular data) to send webhooks to your local n8n instance, an ngrok tunnel is heavily utilized.
Make sure your ngrok tunnel is up and running on port `5678`, matching the `WEBHOOK_URL` configured in `docker-compose.yml`.

### 3. Load the Workflows
If you have a fresh n8n instance or are migrating:
1. Open the n8n UI in your browser.
2. Go to **Workflows** -> **Add Workflow**.
3. Click the `...` menu in the top right and select **Import from File**.
4. Select the `VoiceMemoWorkflow.json` file located in this folder.

## 🎙️ Voice Memo to Notion: Workflow Setup

This specific workflow acts as a smart voice-to-text journal assistant and requires three integrations to function:

1. **iOS Shortcut**:
   - Records audio and base64 encodes the file natively (ensure "Line Breaks" is set to `None`).
   - Sends a `POST` request to your ngrok webhook URL (e.g., `https://<your-ngrok-url>/webhook/VoiceMemo`).
   - The JSON body must contain a key named `"voice"` containing the raw base64 string.
2. **OpenAI Credentials**:
   - Used for the OpenAI Whisper (Transcription) and GPT-4o (Data Extraction) nodes.
   - You must generate an API key from the OpenAI developer dashboard and input it into n8n as a new credential.
3. **Notion Credentials & Database**:
   - Requires a Notion Internal Integration Secret from the Notion dev portal.
   - **Crucial Step**: Your target Notion Journal database must be explicitly shared with your integration via the `...` -> `Connections` menu on the actual Notion page.
   - The final node maps the extracted fields (Title, Summary, Date, Focus Area, etc.) to your Notion database properties.

## 🛑 Stopping the Server
To safely shut down the n8n instance without losing your data or configurations:
```bash
docker compose down
```
Your workflows, credentials, and execution history are safely stored in the `n8n_data` Docker volume and will be exactly where you left them when you start the server again.

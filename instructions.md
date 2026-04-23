# PetroPulse: Render Deployment & Free PostgreSQL Guide

Follow these steps to host your PetroPulse backend on Render and set up a free PostgreSQL database.

## 1. Setup a Free PostgreSQL Database on Render

Render offers a free tier for PostgreSQL that lasts for 90 days per instance (you can recreate it afterwards).

1.  Log in to your [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Database**.
3.  Fill in the details:
    *   **Name**: `petropulse-db`
    *   **Database**: `petropulse`
    *   **User**: (Leave as default or choose one)
    *   **Region**: Select the region closest to you.
    *   **Instance Type**: Select **Free**.
4.  Click **Create Database**.
5.  Wait for the status to show "Available".
6.  Once created, scroll down to find the **Internal Database URL**. You will need this if you manually link services, but our `render.yaml` automates this.

## 2. Deploy Using Render Blueprint (Recommended)

The project includes a `render.yaml` file that automates the creation of both the Web Service and the Database.

1.  Connect your GitHub repository to Render.
2.  On the Render Dashboard, click **New +** and select **Blueprint**.
3.  Select your repository.
4.  Render will detect the `render.yaml` file.
5.  Click **Apply**.
6.  Render will automatically:
    *   Spin up a Free PostgreSQL instance.
    *   Deploy the Backend Web Service.
    *   Automatically connect the `DATABASE_URL` from the DB to the Web Service.

## 3. Manual Web Service Setup (Alternative)

If you prefer to set up the Web Service manually:

1.  Click **New +** and select **Web Service**.
2.  Connect your repository.
3.  Settings:
    *   **Name**: `petropulse-backend`
    *   **Language**: `Python`
    *   **Build Command**: `pip install -r requirements.txt` (Make sure you are in the `backend` directory or adjust path)
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  Go to the **Environment** tab:
    *   Add `DATABASE_URL`: Copy the **Internal Database URL** from your Render Database page.
    *   Add `PYTHON_VERSION`: `3.10.0`
5.  Click **Deploy Web Service**.

## 4. Local Development Connection

To connect to your Render DB from your local machine:

1.  Go to your Database page on Render.
2.  Find the **External Database URL**.
3.  Create a `.env` file in the `backend/` directory.
4.  Add the line: `DATABASE_URL=your_external_url_here`
5.  Run locally: `uvicorn main:app --reload`

> [!CAUTION]
> Never commit your `.env` file with real credentials to GitHub. Use the `.env.example` as a template.

---

### Verification
Once deployed, your backend will be live at `https://your-service-name.onrender.com`. You can test the root endpoint by visiting it in your browser; it should return: `{"message": "PetroPulse API is running"}`.

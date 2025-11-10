# NewsAPI Setup Checklist

Follow these steps before starting Milestone 1 so the news scraper can run without delays.

1. **Create an account**
   - Visit https://newsapi.org/register
   - Sign up with the xseller.ai account email
   - Confirm the email address

2. **Copy the API key**
   - On the NewsAPI dashboard, copy the `API key`
   - Free tier allows 100 requests/day which is enough for M1 testing

3. **Store it in the backend environment file**
   ```bash
   cd backend
   echo "NEWSAPI_KEY=your_key_here" >> .env
   ```
   - Replace `your_key_here` with the real key
   - Do **not** commit `.env`

4. **Verify the key**
   - Run the setup validator (see `backend/verify_setup.py`)
   - You should see `✅ NEWSAPI_KEY present`

5. **Track usage**
   - The free tier resets daily at midnight UTC
   - If rate-limited, switch temporarily to another RSS feed provider

Keep this file updated if we rotate keys or move to a paid tier.

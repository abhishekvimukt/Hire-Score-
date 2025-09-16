
# Hire-Score: An AI-Powered Lead Scoring Service

This backend service tackles the challenge of lead qualification. It intelligently analyzes a list of prospects against a specific product offer, assigning each lead an intent score (**High**, **Medium**, or **Low**) based on a smart combination of fixed rules and dynamic AI analysis.


## Technology Used

* **API Framework:** Django & Django REST Framework
* **Artificial Intelligence:** Google Gemini (`gemini-1.5-flash`)
* **Data Validation:** DRF Serializers
* **Configuration:** Python-Dotenv for managing environment variables

## Running It Locally

Here’s how to get the project set up on your own machine.

#### 1. Grab the Code
First, clone the project from GitHub and navigate into the main directory.
```bash
git clone [https://github.com/abhishekvimukt/Hire-Score-.git](https://github.com/abhishekvimukt/Hire-Score-.git)
cd lead_scorer
```

#### 2. Set Up Your Environment
It's best to use a virtual environment to keep dependencies clean.
```bash
# Create the environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install the necessary packages
pip install -r requirements.txt
```

#### 3. Configure Your API Key
You'll need a Google Gemini API key. Create a `.env` file in the `lead_scorer/` root folder and add your key like this:
```
GOOGLE_API_KEY="AIzaSyCzwObrpumJtQU6fT2gTKXqJFz6N96DFQ4"
```

#### 4. Prepare the Database
Run the initial Django migrations to set up the database.
```bash
python manage.py migrate
```

#### 5. Start the Server
Now you're ready to run the local development server.
```bash
python manage.py runserver
```
The API will be live at `http://127.0.0.1:8000/score/`.

## How to Use the API

You can interact with all endpoints using the `/score/` prefix.

#### 1. Define Your Offer
First, tell the system about your product by sending its details as JSON.
```bash
curl -X POST [http://127.0.0.1:8000/score/offer/](http://127.0.0.1:8000/score/offer/) \
-H "Content-Type: application/json" \
-d '{ "name": "AI Outreach Automation", "value_props": ["24/7 outreach", "6x more meetings"], "ideal_use_cases": ["B2B SaaS mid-market"] }'
```

#### 2. Upload Your Leads
Next, upload your list of prospects as a CSV file.
```bash
curl -X POST [http://127.0.0.1:8000/score/leads/upload/](http://127.0.0.1:8000/score/leads/upload/) \
-F "file=@/path/to/your/leads.csv"
```

#### 3. Trigger the Scoring
Tell the server to start the analysis process on the leads you just uploaded.
```bash
curl -X POST [http://127.0.0.1:8000/score/score/](http://127.0.0.1:8000/score/score/)
```

#### 4. View the Results (JSON)
Retrieve the scored leads as a JSON array.
```bash
curl -X GET [http://127.0.0.1:8000/score/results/](http://127.0.0.1:8000/score/results/)
```

#### 5. Download the Results (CSV)
Export the same results as a downloadable CSV file.
```bash
curl -X GET [http://127.0.0.1:8000/score/results/csv/](http://127.0.0.1:8000/score/results/csv/) --output scored_leads.csv
```

## How the Scoring Works

Each lead's score is a total of two parts: a baseline score from fixed rules and a dynamic score from the AI.

#### The Rule-Based Score (up to 50 points)
* **Job Role Importance (+20 or +10 pts):** We check if the lead's job title contains keywords that identify them as a **decision-maker** (like "ceo", "director") for +20 points, or an **influencer** (like "engineer", "consultant") for +10 points.
* **Industry Fit (+20 or +10 pts):** We check if the lead's industry is a strong match with the offer's `ideal_use_cases` for +20 points. If not, we check for a weaker, **adjacent match** (containing "saas" or "b2b") for +10 points.
* **Profile Completeness (+10 pts):** We award a final +10 points if all the required fields in the lead's profile are filled out.

#### The AI Score (up to 50 points)
The AI's response is converted into points: **High** intent is worth 50 points, **Medium** is 30, and **Low** is 10. This is added to the rule score for the final result.

## The AI Prompt

To get a consistent and useful analysis, we provide the Google Gemini AI with a clear and structured prompt. Here is the template we use:

```
Analyze the following prospect's buying intent for our product.

**Our Product/Offer:**
- Name: {offer.name}
- Value Propositions: {', '.join(offer.value_props)}
- Ideal Use Cases / Target Industry: {', '.join(offer.ideal_use_cases)}

**Prospect Details:**
- Name: {lead.name}
- Role: {lead.role}
- Company: {lead.company}
- Industry: {lead.industry}
- LinkedIn Bio: {lead.linkedin_bio}

**Task:**
Your response MUST be in the following format, with no other text:
Intent: [High/Medium/Low]
Reasoning: [Your 1-2 sentence explanation]
```

## Deployment

This section is reserved for the live API base URL once the application has been deployed to a cloud provider.

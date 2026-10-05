# ShopBot starter application

ShopBot is a deliberately small customer-service chatbot used for a security
homework. It uses synthetic customer and purchase data only.

## Requirements

- Python 3.11 or newer
- An OpenAI API key
- A small API budget/credit balance (the course suggests starting with about $10)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\\Scripts\\activate      # Windows PowerShell
pip install -r requirements.txt
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and replace the placeholder with your own API key.
Never commit this file or your API key to GitHub.

Then run:

```bash
streamlit run app.py
```

The application creates `shopbot.db` automatically the first time it runs.
All names, email addresses, and purchase records are synthetic.

## Deploy on Streamlit Community Cloud

1. Push the repository to your GitHub account/repository used for the course.
2. In Streamlit Community Cloud, create an app from the repository and choose
   `app.py` as the entrypoint.
3. In the deployment's secrets settings, add:

```toml
OPENAI_API_KEY = "sk-..."
```

4. Deploy the application and test it using only the synthetic accounts supplied
   with the starter code.

Do not publish your API key. Do not use real customer information. Because this
application is used for security experiments, do not advertise its URL publicly,
and take it offline when you are not using it if broad Internet access is not
needed.

## Files

- `app.py` - Streamlit user interface and simulated login
- `chatbot.py` - OpenAI Responses API interaction and tool-call loop
- `tools.py` - tool definition and dispatch
- `db.py` - SQLite schema, synthetic data, and data-access functions
- `requirements.txt` - Python dependencies

## Recording and replaying your attacks

For Part III, record your attacks in `attacks.json`. Each entry names the simulated
logged-in customer and contains one or more user messages. A multi-turn attack is
represented by placing several user messages in the `messages` array; ShopBot's
assistant replies are generated automatically between those messages.

A template is included in the starter repository. **You may not modify the structure
of the template**, except to add additional entries having the same structure (with
a different `id`). Replace the placeholder content in each entry with your actual
attack instructions. Do not add, remove, or rename fields in an attack entry. The
provided `run_attacks.py` script and the instructor's evaluation infrastructure expect
this format. In particular, do not add a `success` field or copy model output into
the file. The attack file should describe the experiment; the runner determines what
happened by examining the actual tool trace.

Run your attacks with:

```bash
python run_attacks.py attacks.json
```

The script prints a short summary and writes detailed traces to
`attack-results.json`. The results file is ignored by Git because LLM behavior may
vary from run to run. Your submitted `attacks.json`, however, must be sufficient
for the course staff to replay your attacks.

For Parts IV and V, rerun the same `attacks.json` after modifying your defenses.
A prompt-level defense may reduce how often the model requests another customer's
records. A robust application-level defense should prevent unauthorized records
from being returned even if the model still makes such a request.

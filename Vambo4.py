from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import threading
from pyngrok import ngrok

# Initialize Flask app and allow CORS
app = Flask(__name__)
CORS(app)

# VamboAI Configuration
VAMBO_API_KEY = ""  
VAMBO_TRANSLATE_URL = "https://api.vambo.ai/v1/translate"
VAMBO_LANGUAGE_IDENTIFY_URL = "https://api.vambo.ai/v1/identify/text"

# Function to translate text using VamboAI
def translate_with_vambo(text, target_lang="swh"):
    headers = {
        "Authorization": f"Bearer {VAMBO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "source_lang": "eng",  # Specify English as source
        "target_lang": target_lang  # Target language, e.g., 'swh' for Swahili
    }

    try:
        # Make API request to VamboAI
        response = requests.post(
            VAMBO_TRANSLATE_URL, 
            headers=headers, 
            json=payload,
            timeout=10
        )

        # Debugging: Print response details
        print("\n--- VamboAI Translation Response ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            response_json = response.json()
            # Use the correct key 'output' for the translated text
            translated_text = response_json.get("output")
            if translated_text:
                return translated_text
            else:
                print("Unexpected response format:", response_json)
                return text
        else:
            print(f"Translation failed: Status code {response.status_code}, Response {response.text}")
            return text

    except requests.exceptions.RequestException as e:
        print(f"Translation error (RequestException): {str(e)}")
        return text
    except Exception as e:
        print(f"Translation error (General Exception): {str(e)}")
        return text

# Chat endpoint for user interaction
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        print("\n--- Chat Endpoint Called ---")
        print(f"Received Data: {data}")

        user_message = data.get("message", "").strip().lower()
        selected_language = data.get("language", "eng")  # Get user's selected language

        # Dictionary of responses to handle both English and Swahili prompts
        responses = {
            "menstruation": {
                "eng": "Menstruation is a natural monthly process. It's important to maintain good hygiene.",
                "swh": "Hedhi ni mchakato wa kawaida wa kila mwezi. Ni muhimu kudumisha usafi mzuri."
            },
            "puberty": {
                "eng": "Puberty is when your body undergoes natural changes as you grow into an adult.",
                "swh": "Kipindi cha kubalehe ni wakati mwili wako unapopitia mabadiliko ya kawaida unapokuwa mtu mzima."
            },
            "hygiene": {
                "eng": "Maintaining proper hygiene is important for your health and wellbeing.",
                "swh": "Kudumisha usafi mzuri ni muhimu kwa afya na ustawi wako."
            },
            "sexual health": {
                "eng": "Sexual health includes taking care of your body and being aware of STIs. Always use protection.",
                "swh": "Afya ya uzazi ni pamoja na kutunza mwili wako na kufahamu kuhusu magonjwa ya zinaa. Tumia kinga kila mara."
            },
            "contraception": {
                "eng": "Contraception helps prevent unintended pregnancies. There are different methods including pills, injections, and condoms.",
                "swh": "Uzazi wa mpango husaidia kuzuia ujauzito usiopangwa. Kuna mbinu tofauti ikiwemo vidonge, sindano, na mipira ya kiume."
            },
            "stis": {
                "eng": "STIs are infections passed during sexual contact. It's important to get tested regularly and use protection.",
                "swh": "Magonjwa ya zinaa ni maambukizi yanayopitishwa wakati wa tendo la ndoa. Ni muhimu kupima mara kwa mara na kutumia kinga."
            }
        }

        # Keywords in both English and Swahili for matching purposes
        keywords = {
            "menstruation": ["menstruation", "hedhi"],
            "puberty": ["puberty", "kubalehe"],
            "hygiene": ["hygiene", "usafi"],
            "sexual health": ["sexual health", "afya ya uzazi"],
            "contraception": ["contraception", "uzazi wa mpango"],
            "stis": ["stis", "magonjwa ya zinaa"]
        }

        # Find an appropriate response based on the user's message and selected language
        response = None
        for key, keywords_list in keywords.items():
            if any(keyword in user_message for keyword in keywords_list):
                response = responses[key].get(selected_language)
                break

        # Default response if no match is found
        if not response:
            if selected_language == "swh":
                response = "Ninaweza kukusaidiaje kwa habari kuhusu hedhi, kubalehe, au usafi?"
            else:
                response = "How can I help you with information about menstruation, puberty, or hygiene?"

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# HTML template for chatbot UI (unchanged)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SexAI Info Bot</title>
    <style>
        body { 
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
        }
        .chat-container {
            width: 90%;
            max-width: 800px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 10px;
            border-bottom: 1px solid #eee;
            margin-bottom: 20px;
        }
        .header h2 {
            color: #1a73e8;
            margin: 0;
        }
        #chat-box {
            height: 500px;
            padding: 15px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f8f9fa;
            margin-bottom: 20px;
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #1a73e8;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        .bot-message {
            background-color: #e9ecef;
            color: #000;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        #input-container {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        #user-input {
            flex-grow: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            font-size: 16px;
        }
        #user-input:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 2px rgba(26,115,232,0.2);
        }
        #send-button {
            padding: 12px 24px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        #send-button:hover {
            background-color: #1557b0;
        }
        #language-select {
            width: 100%;
            margin-bottom: 20px;
            padding: 10px;
            font-size: 16px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h2>SexAI Info Bot</h2>
        </div>
        
        <div>
            <select id="language-select">
                <option value="eng">English</option>
                <option value="swh">Swahili</option>
            </select>
        </div>

        <div id="chat-box"></div>
        
        <div class="controls">
            <div id="input-container">
                <input type="text" 
                       id="user-input" 
                       placeholder="Type your message here..."
                       autocomplete="off">
                <button id="send-button" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let isProcessing = false;
        let selectedLanguage = "eng"; // Default to English

        document.getElementById('language-select').addEventListener('change', function() {
            selectedLanguage = this.value;
            console.log("Selected Language:", selectedLanguage);
        });

        function addMessage(message, isUser, isError = false) {
            const chatBox = document.getElementById('chat-box');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            if (isError) messageDiv.className += ' error-message';
            messageDiv.textContent = message;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
            return messageDiv;
        }

        async function sendMessage() {
            if (isProcessing) return;

            const input = document.getElementById('user-input');
            const message = input.value.trim();

            if (!message) return;

            isProcessing = true;
            input.value = '';
            addMessage(message, true);

            const loadingMessage = addMessage('Typing...', false);

            try {
                // Send request to the backend
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        language: selectedLanguage
                    })
                });

                const data = await response.json();
                loadingMessage.remove();

                if (data.error) {
                    addMessage('Sorry, an error occurred. Please try again.', false, true);
                } else {
                    addMessage(data.response, false);
                }
            } catch (error) {
                loadingMessage.remove();
                addMessage('Network error. Please check your connection.', false, true);
                console.error('Error:', error);
            } finally {
                isProcessing = false;
            }
        }

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isProcessing) {
                sendMessage();
            }
        });

        // Initial message
        window.onload = function() {
            addMessage('Karibu! Tafadhali chagua lugha yako na uulize swali kuhusu hedhi, kubalehe, au afya kwa ujumla. Welcome! Please select your language and ask a question about menstruation, puberty, or general health.', false);
        };
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

def start_flask():
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

if __name__ == "__main__":
    try:
        # Set ngrok auth token and start the tunnel
        ngrok.set_auth_token("7UwjSLDsGNXaFACKATwxe_3h2jYUS7u5RXz34mVske4")
        public_url = ngrok.connect(5001)
        print(f"Bot is accessible at: {public_url}")

        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=start_flask)
        flask_thread.start()

        print("Bot is running! Press Ctrl+C to stop.")
        flask_thread.join()

    except KeyboardInterrupt:
        print("Shutting down the bot...")
        ngrok.disconnect(public_url)
    except Exception as e:
        print(f"An error occurred: {e}")

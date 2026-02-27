# ECE-NLP-49595-59595-HW-1
A pair of chatbots, one arguing as Donald Trump and the other as Joe Biden
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies (first time only)
pip install -r requirements.txt

# Run debate (pick one per laptop)
python main.py biden
python main.py trump

# Test API responses without speech
python test.py

# Test speech output only
python -c "from speech import speak_output; speak_output.start(); speak_output.say('Hello'); import time; time.sleep(5)"

# Test speech input only
python -m speech.speech_to_text_microsoft

# Deactivate virtual environment
deactivate
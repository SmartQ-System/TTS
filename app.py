"""
SmartQ TTS Microservice
Edge TTS Python service for Arabic text-to-speech
"""

import asyncio
import io
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import edge_tts

app = Flask(__name__)
CORS(app)

# Available Arabic voices
ARABIC_VOICES = [
    {"id": "ar-EG-ShakirNeural", "name": "شاكر", "gender": "male", "locale": "مصر"},
    {"id": "ar-EG-SalmaNeural", "name": "سلمى", "gender": "female", "locale": "مصر"},
    {"id": "ar-SA-HamedNeural", "name": "حامد", "gender": "male", "locale": "السعودية"},
    {"id": "ar-SA-ZariyahNeural", "name": "زارية", "gender": "female", "locale": "السعودية"},
    {"id": "ar-AE-FatimaNeural", "name": "فاطمة", "gender": "female", "locale": "الإمارات"},
    {"id": "ar-AE-HamdanNeural", "name": "حمدان", "gender": "male", "locale": "الإمارات"},
]


async def generate_tts(text: str, voice: str) -> bytes:
    """Generate TTS audio using edge-tts"""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = io.BytesIO()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    
    audio_data.seek(0)
    return audio_data.getvalue()


@app.route('/api/tts/speak', methods=['POST'])
def speak():
    """Convert text to speech"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
    
    text = data['text']
    voice = data.get('voice', 'ar-EG-ShakirNeural')
    
    # Validate voice
    valid_voices = [v['id'] for v in ARABIC_VOICES]
    if voice not in valid_voices:
        voice = 'ar-EG-ShakirNeural'
    
    try:
        print(f"[TTS] Generating speech for: {text[:30]}... with voice: {voice}")
        audio_bytes = asyncio.run(generate_tts(text, voice))
        print(f"[TTS] Generated {len(audio_bytes)} bytes")
        
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/mp3',
            as_attachment=True,
            download_name='speech.mp3'
        )
    except Exception as e:
        print(f"[TTS] Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tts/voices', methods=['GET'])
def get_voices():
    """Get available Arabic voices"""
    return jsonify({
        "success": True,
        "voices": ARABIC_VOICES
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "OK", "service": "TTS Microservice"})


if __name__ == '__main__':
    print("""
🎤 SmartQ TTS Microservice
--------------------------
📡 Port: 5001
🔗 API: http://localhost:5001/api/tts/speak
📚 Voices: http://localhost:5001/api/tts/voices
--------------------------
    """)
    app.run(host='0.0.0.0', port=5001, debug=True)

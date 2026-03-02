from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import wave
from vosk import Model, KaldiRecognizer
from transformers import MarianMTModel, MarianTokenizer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "vosk-model-small-en-us-0.15")

vosk_model = Model(model_path)

model_name = "Helsinki-NLP/opus-mt-en-hi"
tokenizer = MarianTokenizer.from_pretrained(model_name)
translator = MarianMTModel.from_pretrained(model_name)

def translate(text):
    tokens = tokenizer(text, return_tensors="pt", padding=True)
    translated = translator.generate(**tokens)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def home(request):
    return JsonResponse({"message": "Voice Translator API. Use POST /voice/translate/ with audio file."})

@csrf_exempt
def translate_audio(request):
    if request.method == "POST":
        try:
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return JsonResponse({"error": "No audio file provided"}, status=400)

            wf = wave.open(audio_file, "rb")
            rec = KaldiRecognizer(vosk_model, wf.getframerate())

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)

            result = json.loads(rec.FinalResult())
            text = result.get("text", "")
            translated = translate(text)

            return JsonResponse({
                "original": text,
                "translated": translated
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are supported"}, status=405)
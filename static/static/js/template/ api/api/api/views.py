import os
import re
import json
import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Flashcard, VideoLink, Textbook
from .serializers import FlashcardSerializer, VideoLinkSerializer, TextbookSerializer, UserSerializer

User = get_user_model()

HF_API_TOKEN = os.environ.get('HF_API_TOKEN')
HF_MODEL = os.environ.get('HF_MODEL')  # optional

HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else None

def generate_flashcards_from_text(notes, max_cards=12):
    notes = (notes or '').strip()
    if not notes:
        return []
    # try Hugging Face inference if configured
    if HF_API_TOKEN and HF_MODEL:
        try:
            url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
            payload = {"inputs": notes}
            resp = requests.post(url, json=payload, headers=HF_HEADERS, timeout=30)
            data = resp.json()
            text_out = ''
            if isinstance(data, list):
                for it in data:
                    if isinstance(it, dict):
                        text_out += (it.get('generated_text') or '') + '\n'
                    else:
                        text_out += str(it) + '\n'
            elif isinstance(data, dict) and data.get('generated_text'):
                text_out = data.get('generated_text')
            elif isinstance(data, str):
                text_out = data
            else:
                text_out = json.dumps(data)
            lines = [l.strip() for l in re.split(r"\n+", text_out) if l.strip()]
            cards = []
            for line in lines:
                if ':' in line:
                    q, a = line.split(':', 1)
                    cards.append({'question': q.strip(), 'answer': a.strip()})
                else:
                    half = len(line) // 2
                    cards.append({'question': line[:half].strip() or line, 'answer': line[half:].strip() or line})
                if len(cards) >= max_cards:
                    break
            if cards:
                return cards
        except Exception:
            pass
    # fallback: split into sentences and make explain cards
    sentences = re.split(r'(?<=[.!?])\s+', notes)
    cards = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        short = ' '.join(s.split()[:8])
        q = f"Explain: {short}..."
        a = s
        cards.append({'question': q, 'answer': a})
        if len(cards) >= max_cards:
            break
    return cards

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        if not username or not password:
            return Response({'error': 'username and password required'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'username taken'}, status=400)
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return Response({'user': UserSerializer(user).data})

class GenerateView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        notes = request.data.get('notes', '')
        cards = generate_flashcards_from_text(notes, max_cards=20)
        return Response({'flashcards': cards})

class FlashcardListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cards = Flashcard.objects.filter(user=request.user).order_by('-created_at')
        return Response({'flashcards': FlashcardSerializer(cards, many=True).data})
    def post(self, request):
        cards = request.data.get('flashcards', [])
        saved = []
        for c in cards:
            fc = Flashcard.objects.create(user=request.user, question=c.get('question',''), answer=c.get('answer',''))
            saved.append(FlashcardSerializer(fc).data)
        return Response({'saved': saved})

class VideoListCreateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        vs = VideoLink.objects.all().order_by('-created_at')
        return Response({'videos': VideoLinkSerializer(vs, many=True).data})
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({'error':'auth required'}, status=401)
        title = request.data.get('title')
        url = request.data.get('url')
        if not title or not url:
            return Response({'error':'title and url required'}, status=400)
        v = VideoLink.objects.create(title=title, url=url)
        return Response({'video': VideoLinkSerializer(v).data})

class TextbookListCreateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        t = Textbook.objects.all().order_by('-created_at')
        return Response({'textbooks': TextbookSerializer(t, many=True, context={'request': request}).data})
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({'error':'auth required'}, status=401)
        file = request.FILES.get('file')
        if not file:
            return Response({'error':'file missing'}, status=400)
        title = request.data.get('title') or file.name
        author = request.data.get('author', '')
        tb = Textbook.objects.create(title=title, author=author, file=file)
        return Response({'textbook': TextbookSerializer(tb, context={'request': request}).data})

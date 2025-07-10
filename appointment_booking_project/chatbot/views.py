from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ChatMessage
from .utils import chat_with_ollama


@csrf_exempt

def chatbot_response(request):
    if request.method == 'POST':
        user_msg = request.POST.get('message','')
        if not request.session.session_key:
            request.session.save()  # forces creation of a session
            
        session_id = request.session.session_key or request.session.create()
        
        # save user message
        ChatMessage.objects.create(session_id = session_id, sender = 'user', message = user_msg)
        
        # bot logic 
        if user_msg.strip().lower() == 'merci':
            bot_msg = 'For more information, create an account and schedule an appointment. We look forward to hearing from you! See you soon!'
        else:
            bot_msg = f" you said : {user_msg}"
                        # Use Ollama API for intelligent response
            prompt = f"User: {user_msg}\nAssistant:"
            bot_msg = chat_with_ollama(prompt, model="llama3")
            
        # save bot response
        ChatMessage.objects.create(session_id = session_id, sender = 'bot', message = bot_msg)
        
        return JsonResponse({'response' : bot_msg})
    return JsonResponse({'response' : 'Non authorized '}, status = 405)

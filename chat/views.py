from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatSession, ChatMessage
from .services import process_document, search_document
import os

def new_chat(request):
    """Creates a new chat session."""
    # CLEANUP: Delete any previous empty chats (New Conversations with no messages)
    # This prevents the "New Conversation" spam in your sidebar
    ChatSession.objects.filter(title="New Conversation", messages__isnull=True).delete()
    
    session = ChatSession.objects.create(title="New Conversation")
    return redirect('chat_session', session_id=session.id)

def delete_chat(request, session_id):
    """Deletes a chat and its associated PDF file."""
    session = get_object_or_404(ChatSession, id=session_id)
    session.delete() # The model's delete() method will handle the file removal
    return redirect('new_chat')

def chat_view(request, session_id=None):
    # 1. Sidebar: Get all sessions
    all_sessions = ChatSession.objects.order_by('-created_at')

    # 2. Determine Current Session
    if session_id:
        current_session = get_object_or_404(ChatSession, id=session_id)
    else:
        if not all_sessions.exists():
            return redirect('new_chat')
        current_session = all_sessions.first()

    # 3. Handle User Input
    if request.method == 'POST':
        
        # SCENARIO A: User Uploads PDF
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            
            # Save file to the Database Model
            current_session.pdf_file = uploaded_file
            current_session.save()
            
            # Process the file using the path from the database
            # Note: This file is now in a folder called 'uploads/'
            file_path = current_session.pdf_file.path
            
            success, msg = process_document(file_path)
            
            # ... inside SCENARIO A.2 ...

            if success:
                # 1. Construct the File URL
                pdf_url = current_session.pdf_file.url

                # 2. Create a "Card" HTML for the message
                # We use onclick to trigger the JavaScript modal we will write next
                card_html = f"""
                <div class="pdf-card" onclick="openPDFViewer('{pdf_url}')">
                    <div class="pdf-icon">📄</div>
                    <div class="pdf-info">
                        <span class="pdf-name">{uploaded_file.name}</span>
                        <span class="pdf-hint">Click to Review PDF</span>
                    </div>
                </div>
                """

                ChatMessage.objects.create(
                    session=current_session,
                    role='ai',
                    content=card_html  # We save the HTML card directly
                )

                # Rename Chat
                current_session.title = uploaded_file.name
                current_session.save()

        # SCENARIO B: User Asks Question
        elif 'query' in request.POST:
            user_query = request.POST['query']
            
            ChatMessage.objects.create(session=current_session, role='user', content=user_query)
            
            # Intelligent Search
            ai_response = search_document(user_query)
            
            ChatMessage.objects.create(session=current_session, role='ai', content=ai_response)
            
            # Rename if it's still "New Conversation"
            if current_session.title == "New Conversation":
                current_session.title = user_query[:30] + "..."
                current_session.save()

        return redirect('chat_session', session_id=current_session.id)

    # 4. Render
    messages = current_session.messages.all()
    context = {
        'chat_sessions': all_sessions,
        'current_session': current_session,
        'messages': messages
    }
    return render(request, 'chat/chat.html', context)
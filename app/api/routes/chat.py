from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Conversation, Goal, Message, User
from app.schemas import ChatRequest, ChatResponse, ConversationResponse
from app.services import openrouter_service, qdrant_service

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = """You are JetAide, a supportive AI assistant that helps people achieve their personal goals like quitting smoking, eating healthier, exercising more, or any other positive life change.

Your role is to:
- Be encouraging and empathetic, understanding that change is hard
- Provide practical, actionable advice
- Celebrate small wins and progress
- Help users identify triggers and develop coping strategies
- Remember context from previous conversations to provide personalized support
- Never be judgmental about setbacks - they're part of the journey

When the user shares information about their goals or progress, acknowledge it and offer relevant support.

User's current goals:
{goals}

Relevant context from previous conversations:
{context}
"""


async def build_system_prompt(user_id: str, query: str, db: AsyncSession) -> str:
    """Build the system prompt with user's goals and relevant memories."""
    # Get user's goals
    result = await db.execute(
        select(Goal).where(Goal.user_id == user_id, Goal.status == "active")
    )
    goals = result.scalars().all()
    goals_text = "\n".join([f"- {g.title} ({g.category}): {g.description or 'No description'}" for g in goals])
    if not goals_text:
        goals_text = "No active goals set yet."

    # Get relevant memories
    try:
        memories = await qdrant_service.search_memories(user_id, query, limit=3)
        context_text = "\n".join([f"- {m['content']}" for m in memories])
    except Exception:
        context_text = "No previous context available."

    if not context_text:
        context_text = "No previous context available."

    return SYSTEM_PROMPT.format(goals=goals_text, context=context_text)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current user."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get a response."""
    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.commit()

    # Build messages for LLM
    system_prompt = await build_system_prompt(current_user.id, request.message, db)

    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history = result.scalars().all()

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-20:]:  # Last 20 messages for context
        messages.append({"role": msg.role, "content": msg.content})

    # Get response from LLM
    response_text = await openrouter_service.chat(messages)

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
    )
    db.add(assistant_message)

    # Update conversation title if it's new
    if not conversation.title and len(history) <= 2:
        conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")

    await db.commit()

    # Store the exchange in vector memory for future context
    try:
        memory_content = f"User: {request.message}\nAssistant: {response_text}"
        await qdrant_service.store_memory(current_user.id, memory_content)
    except Exception:
        pass  # Don't fail the request if memory storage fails

    return ChatResponse(response=response_text, conversation_id=conversation.id)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and stream the response."""
    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.commit()

    # Build messages for LLM
    system_prompt = await build_system_prompt(current_user.id, request.message, db)

    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history = result.scalars().all()

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-20:]:
        messages.append({"role": msg.role, "content": msg.content})

    async def generate():
        full_response = []
        async for chunk in openrouter_service.chat_stream(messages):
            full_response.append(chunk)
            yield f"data: {chunk}\n\n"

        # Store assistant message after streaming completes
        response_text = "".join(full_response)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
        )
        db.add(assistant_message)

        if not conversation.title:
            conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")

        await db.commit()

        # Store in memory
        try:
            memory_content = f"User: {request.message}\nAssistant: {response_text}"
            await qdrant_service.store_memory(current_user.id, memory_content)
        except Exception:
            pass

        yield f"data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()
    return {"message": "Conversation deleted"}

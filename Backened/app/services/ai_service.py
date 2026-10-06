import asyncio

from app.services.llm_service import llm_service

async def auto_prioritize_tasks(tasks_list: list) -> str:
    prompt = f"""
    You are an AI Executive Assistant. Analyze the following user tasks:
    {tasks_list}

    Perform 2 actions:
    1. Prioritize these tasks into High, Medium, and Low urgency.
    2. Give a brief 2-sentence strategy for the user to complete them efficiently today.
    """

    return await asyncio.to_thread(llm_service.generate_completion, prompt)

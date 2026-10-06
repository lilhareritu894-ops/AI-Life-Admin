from app.services.llm_service import llm_service

class CalendarAgent:
    def resolve_schedule_conflict(self, events: str) -> str:
        prompt = f"Identify conflicts and suggest optimal times for these events:\n{events}"
        return llm_service.generate_completion(prompt)

calendar_agent = CalendarAgent()
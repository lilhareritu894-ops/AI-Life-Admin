from app.services.llm_service import llm_service

class TaskAgent:
    def auto_generate_subtasks(self, task_title: str) -> str:
        prompt = f"Break down the following life admin task into 3 short actionable sub-steps: '{task_title}'"
        return llm_service.generate_completion(prompt)

task_agent = TaskAgent()
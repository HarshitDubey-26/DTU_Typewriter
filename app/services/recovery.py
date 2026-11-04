"""Check for recoverable typing drafts on application startup."""
import logging

logger = logging.getLogger("dtu_typewriter.recovery")


class RecoveryService:
    def __init__(self, controller):
        self.controller = controller

    def check_for_draft(self, student_id: int):
        logger.info(
            "Checking for recoverable draft for student %s", student_id
        )
        self.controller.load_draft(student_id)

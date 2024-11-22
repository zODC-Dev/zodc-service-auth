from src.app.services.event_service import event_service

class EventController:
    async def get_events(self):
        return await event_service.get_events()
    
event_controller = EventController()
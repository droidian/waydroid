from dbus_next.service import ServiceInterface, signal

class INotification(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)

    @signal()
    def NewMessage(self, app_name: 's', count: 'i') -> 'as':
        return [app_name, str(count)]

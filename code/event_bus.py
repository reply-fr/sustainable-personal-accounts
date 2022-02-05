import logging


class EventFactory:

    @classmethod
    def emit(cls, label, account):
        event = cls.build_event(label, account)
        cls.put_event(event)

    @classmethod
    def build_event(cls, label, account):
        return dict(label=label, account_id=account)

    @classmethod
    def put_event(cls, event):
        logging.info(f'put_event: {event}')

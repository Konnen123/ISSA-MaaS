def _generate_token():
    import uuid
    return str(uuid.uuid4())


class SessionService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionService, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init_once__()
        return cls._instance

    def __init_once__(self):
        self.sessions = {}

    def create_session(self, user):
        token = _generate_token()
        self.sessions[token] = user
        return token

    def get_user(self, token):
        return self.sessions.get(token)

    def delete_session(self, token):
        if token in self.sessions:
            del self.sessions[token]

    @property
    def instance(self):
        return self._instance


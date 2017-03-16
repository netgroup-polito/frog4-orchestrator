from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.sql.user import UserTokenModel

class users_tokens_clean():
    def token_clean(self):
        session = get_session()
        session.query(UserTokenModel).delete()
        return ("Table (user_token) has been cleaned up")

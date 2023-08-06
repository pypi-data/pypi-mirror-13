from flask_pundit.application_policy import ApplicationPolicy


class PostPolicy(ApplicationPolicy):
    def get(self):
        return self.user.get('role') == 'admin'

    def create(self):
        return self.user.get('role') == 'admin'

    class Scope(ApplicationPolicy.Scope):
        def resolve(self):
            if self.user.get('role') == 'admin':
                return [1, 2]
            return [3, 4]

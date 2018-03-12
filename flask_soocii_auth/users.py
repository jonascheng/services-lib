class User:
    @property
    def is_backstage(self):
        return False


class AnonymousUser(User):
    pass


class SoociiGuest(User):
    pass


class BackstageUser(User):
    @property
    def is_backstage(self):
        return True

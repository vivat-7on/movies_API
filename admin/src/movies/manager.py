from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, login: str, password: str = None):
        if not login:
            raise ValueError("Login is required")

        user = self.model(login=login)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login: str, password: str = None):
        user = self.create_user(login, password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user

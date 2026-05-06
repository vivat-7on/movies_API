import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.manager import MyUserManager


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FilmType(models.TextChoices):
    MOVIE = "movie", _("Movie")
    TV_SHOW = "tv_show", _("TV show")


class FilmWork(UUIDMixin, TimestampMixin):
    title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
        null=False,
        blank=False,
    )
    description = models.TextField(verbose_name=_("description"), blank=True)
    creation_date = models.DateField(
        verbose_name=_("creation date"),
        null=True,
        blank=True,
    )
    rating = models.FloatField(verbose_name=_("rating"), null=True, blank=True)
    type = models.CharField(
        verbose_name=_("type"),
        choices=FilmType.choices,
        default=FilmType.MOVIE,
        max_length=20,
    )
    genres = models.ManyToManyField("Genre", through="GenreFilmWork")
    persons = models.ManyToManyField("Person", through="PersonFilmWork")

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'content"."film_work'
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"


class Genre(UUIDMixin, TimestampMixin):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
        null=False,
        blank=False,
    )
    description = models.TextField(verbose_name=_("description"), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'content"."genre'
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Person(UUIDMixin, TimestampMixin):
    full_name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        managed = False
        db_table = 'content"."person'
        verbose_name = "Актёр"
        verbose_name_plural = "Актёры"


class GenreFilmWork(UUIDMixin, TimestampMixin):
    genre = models.ForeignKey(
        "Genre",
        on_delete=models.CASCADE,
        db_column="genre_id",
    )
    film_work = models.ForeignKey(
        "FilmWork",
        on_delete=models.CASCADE,
        db_column="film_work_id",
    )

    class Meta:
        managed = False
        db_table = 'content"."genre_film_work'


class PersonFilmWork(UUIDMixin, TimestampMixin):
    person = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        db_column="person_id",
    )
    film_work = models.ForeignKey(
        "FilmWork",
        on_delete=models.CASCADE,
        db_column="film_work_id",
    )
    role = models.TextField(verbose_name="role")

    class Meta:
        managed = False
        db_table = 'content"."person_film_work'


class User(AbstractBaseUser, UUIDMixin, TimestampMixin):
    login = models.CharField(unique=True, max_length=255)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    @property
    def is_staff(self):
        return self.is_admin

    USERNAME_FIELD = "login"

    objects = MyUserManager()

    def __str__(self):
        return f"{self.login} {self.id}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

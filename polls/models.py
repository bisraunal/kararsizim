from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class Poll(models.Model):
    CATEGORY_CHOICES = [
        ('genel', 'Genel'),
        ('yemek', 'Yemek & Mutfak'),
        ('teknoloji', 'Teknoloji & Cihazlar'),
        ('moda', 'Moda & Stil'),
        ('dizi-film', 'Dizi & Film'),
        ('oyun', 'Oyun & Espor'),
        ('egitim', 'Eğitim & Kariyer'),
        ('alisveris', 'Alışveriş'),
        ('spor', 'Spor & Fitness'),
        ('diger', 'Diğer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls', verbose_name='Oluşturan')
    question = models.CharField(max_length=250, verbose_name='Soru / Başlık')
    description = models.TextField(blank=True, null=True, verbose_name='Açıklama / Bağlam')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='genel', verbose_name='Kategori')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'

    def __str__(self):
        return self.question

    @property
    def total_votes(self):
        return self.votes.count()

    def user_has_voted(self, user=None, session_key=None):
        """Checks if a user (or guest session) has already voted in this poll."""
        if user and user.is_authenticated:
            return self.votes.filter(user=user).exists()
        elif session_key:
            return self.votes.filter(session_key=session_key).exists()
        return False

    def get_user_vote(self, user=None, session_key=None):
        """Returns the Vote object for the given user or session, if any."""
        if user and user.is_authenticated:
            return self.votes.filter(user=user).first()
        elif session_key:
            return self.votes.filter(session_key=session_key).first()
        return None


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options', verbose_name='Bağlı Anket')
    text = models.CharField(max_length=200, verbose_name='Seçenek Metni')
    order = models.PositiveSmallIntegerField(default=1, verbose_name='Sıra')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Seçenek'
        verbose_name_plural = 'Seçenekler'

    def __str__(self):
        return f"{self.poll.question} -> {self.text}"

    @property
    def vote_count(self):
        return self.votes.count()

    @property
    def vote_percentage(self):
        total = self.poll.total_votes
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes', verbose_name='Anket')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes', verbose_name='Seçilen Seçenek')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cast_votes', verbose_name='Kullanıcı')
    session_key = models.CharField(max_length=100, null=True, blank=True, verbose_name='Misafir Oturum Anahtarı')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oy Tarihi')

    class Meta:
        verbose_name = 'Oy'
        verbose_name_plural = 'Oylar'
        constraints = [
            models.UniqueConstraint(
                fields=['poll', 'user'],
                condition=Q(user__isnull=False),
                name='unique_user_poll_vote'
            ),
            models.UniqueConstraint(
                fields=['poll', 'session_key'],
                condition=Q(session_key__isnull=False),
                name='unique_session_poll_vote'
            ),
        ]

    def __str__(self):
        voter = f"@{self.user.username}" if self.user else f"Misafir ({self.session_key})"
        return f"{voter} -> {self.option.text} ({self.poll.question})"

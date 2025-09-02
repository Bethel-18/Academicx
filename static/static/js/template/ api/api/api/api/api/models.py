from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.question[:60] + '...') if len(self.question) > 60 else self.question

class VideoLink(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Textbook(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='textbooks/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

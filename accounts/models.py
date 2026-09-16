from django.db import models
from django.contrib.auth.models import User


class JapRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    target = models.PositiveIntegerField(default=108)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def progress(self):
        if self.target == 0:
            return 0
        return min(int((self.count / self.target) * 100), 100)
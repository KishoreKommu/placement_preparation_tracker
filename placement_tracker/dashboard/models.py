from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    LEVEL_CHOICES = [
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    name = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)  # %

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


class UserGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} goal: {self.skill.name}"
    

class MockTest(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MockTestQuestion(models.Model):
    test = models.ForeignKey(MockTest, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)  # the correct option

    def __str__(self):
        return f"{self.test.name} - {self.question[:50]}"


class UserMockTest(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    test = models.ForeignKey(MockTest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.test.name} ({self.score})"
    

from django.db import models
from django.contrib.auth.models import User

class UserResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Resume"


from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    skillset = models.TextField(blank=True)
    positions = models.TextField(blank=True)
    tasks = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class UpcomingBattle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    deadline = models.DateField()


from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leetcode_id = models.CharField(max_length=100, blank=True)
    gfg_id = models.CharField(max_length=100, blank=True)




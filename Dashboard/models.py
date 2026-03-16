from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Skill(models.Model):

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    level = models.CharField(max_length=100, default="Intermediate")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    


# dashboard/models.py

class MockTest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    # other fields...


class MockTestQuestion(models.Model):
    test = models.ForeignKey(MockTest, related_name="questions", on_delete=models.CASCADE)

    question = models.TextField()

    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)

    answer = models.CharField(max_length=200)

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
    action = models.CharField(max_length=50, blank=True, null=True)
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



class CareerPath(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    pdf = models.FileField(upload_to='career_paths/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

from django.db import models
from django.contrib.auth.models import User

class Opportunity(models.Model):
    OPPORTUNITY_TYPES = (
        ('JOB', 'Full-time Job'),
        ('INT', 'Internship'),
        ('FRE', 'Freelance'),
    )
    
    tier_choices = (
        ('T1', 'Tier 1 (FAANG/Top Product)'),
        ('T2', 'Tier 2 (Mid-Level Product)'),
        ('T3', 'Tier 3 (Service Based)'),
    )

    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_logo_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, default="Remote")
    opp_type = models.CharField(max_length=3, choices=OPPORTUNITY_TYPES, default='JOB')
    tier = models.CharField(max_length=2, choices=tier_choices, default='T2')
    
    description = models.TextField()
    requirements = models.TextField(help_text="Comma separated skills")
    
    package_details = models.CharField(max_length=100, help_text="e.g., 12-15 LPA or 25k/month")
    deadline = models.DateTimeField()
    apply_link = models.URLField()
    
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.company_name} - {self.title}"

class SavedOpportunity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)




from django.db import models

# Create your models here.

class Offer(models.Model):
    name = models.CharField(max_length=255)
    value_props = models.JSONField(default=list)  # Stores a list of strings
    ideal_use_cases = models.JSONField(default=list)  # Stores a list of strings
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Lead(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin_bio = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company})"

class ScoreResult(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    intent = models.CharField(max_length=50) # High, Medium, Low
    score = models.IntegerField()
    reasoning = models.TextField()
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score for {self.lead.name} on {self.offer.name}: {self.intent} ({self.score})"
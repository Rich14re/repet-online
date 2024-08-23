# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    required_status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    grade = models.CharField(max_length=10, default='6class')

    def __str__(self):
        return self.title

class Explain(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    statuses = models.ManyToManyField(Status, blank=True)

    def __str__(self):
        return f'Profile for {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ComputerScienceTask(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class ComputerScienceTaskDetail(models.Model):
    task = models.ForeignKey(ComputerScienceTask, related_name='details', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='computer_science_task_images/', blank=True, null=True)
    video = models.FileField(upload_to='computer_science_task_videos/', blank=True, null=True)

    def __str__(self):
        return f"Detail for {self.task.title}"


class Task(models.Model):
    course = models.ForeignKey(Course, related_name='tasks', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    correct_answer = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    video = models.FileField(upload_to='task_videos/', blank=True, null=True)
    is_theory = models.BooleanField(default=False)
    
    expl = models.TextField(blank=True, null=True)
    expl_img = models.ImageField(upload_to='task_images/', blank=True, null=True)
    expl_video = models.FileField(upload_to='task_videos/', blank=True, null=True)
    
    file = models.FileField(upload_to='task_videos/', blank=True, null=True)
    file_link_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.description[:50]

class Explanation(models.Model):
    explain = models.ForeignKey(Explain, related_name='explains', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    video = models.FileField(upload_to='task_videos/', blank=True, null=True)

    def __str__(self):
        return self.description[:50]

# class Explanation(models.Model):
    # explain = models.ForeignKey(Explain, on_delete=models.CASCADE, related_name='descriptions', default=1)
    # description = models.TextField()
    # media = models.FileField(upload_to='media/')

    # def __str__(self):
        # return self.description[:50]

class UserTaskStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    answer = models.CharField(max_length=200, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    total_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.description[:50]} - {'Correct' if self.is_correct else 'Incorrect'}"

class Class(models.Model):
    grade = models.IntegerField()

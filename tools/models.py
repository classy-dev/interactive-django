import os

from django.db import models
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel
from backtest.models import Rule, RuleCombination, PrimaryRule, Indicator
# Create your models here.

#UNIVERSE MODEL
class Universe_Tree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)

    def __str__(self):
        return self.child_name


class Universe_Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    parent_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Universe_Universe(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    parent_path = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.name

class Universe_Default(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='universe/')
    count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def filename(self):
        return os.path.basename(self.file.name)
    def __str__(self):
        return self.title


#LISTS MODEL
class Lists_Tree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Lists_Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    parent_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Lists_Universe(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    parent_path = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.name

class Lists_Default(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='lists/')
    count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def filename(self):
        return os.path.basename(self.file.name)


#BENCHMARKS MODEL
class Benchmarks_Tree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.child_name


class Benchmarks_Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    parent_id = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Benchmarks_Universe(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    parent_path = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.name

class Benchmarks_Default(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='benchmarks/')
    count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def filename(self):
        return os.path.basename(self.file.name)

#RANKING SYSTEM MODEL

class Ranking_Rule(PolymorphicModel):
    Direction_type = {
        ('HB', 'Higher is better'),
        ('LB', 'Lower is better'),
    }
    weight = models.FloatField(max_length=5)
    indicator = models.ForeignKey(Indicator, related_name="indicator", on_delete=models.CASCADE)
    name = models.CharField(max_length=100,)
    direction = models.CharField("Direction", max_length=20, choices=Direction_type)
    rank_id = models.IntegerField()
    def __str__(self):
        return self.name

class Ranking_System(models.Model):
    name = models.CharField(max_length=100)
    rule = models.ManyToManyField(Ranking_Rule, related_name="rules+")
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Ranking_Tree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Ranking_Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    def __str__(self):
        return self.name


#LIQUIDITY_SYSTEM MODEL

class Liquidity_Tree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Liquidity_Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Liquidity_Rule(models.Model):
    min_amount = models.IntegerField()
    max_amount = models.IntegerField()
    rule = models.ForeignKey(PrimaryRule, related_name='liquidity_rule', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Liquidity_System(models.Model):
    name = models.CharField(max_length=100)
    rule = models.ManyToManyField(Rule, related_name="backtestrules++")
    rulecombination = models.ManyToManyField(RuleCombination, related_name='rulecombinations+')
    liquidity_rule = models.ManyToManyField(Liquidity_Rule, related_name="liquidityrule+")
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    def get_rules(self):
        return self.rule.all()  
    def get_rule_combinations(self):
        return self.rulecombination.all()
    def get_liquidity_rules(self):
        return self.liquidity_rule.all()
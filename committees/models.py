import os

from django.contrib.auth.models import User
from django.db import models


position_paper_upload_path = 'position-papers/'

def get_position_paper_path(instance, filename):
    return os.path.join(position_paper_upload_path, str(instance.id) + os.path.splitext(filename)[1])


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.name


class Committee(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category)
    # Committees should be hidden until they are released
    is_visible = models.BooleanField(default=False)
    # Used for ensuring committee assignments for joint committees go to the
    # specific side of the joint, not the umbrella committee.
    is_assignable = models.BooleanField(default=True)
    # The user (usually [slug]@mcmun.org) who can manage this committee.
    manager = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        ordering = ('category', 'id')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('committee_view', [self.slug])

    def allow_manager(self, user):
        return self.manager == user or user.is_staff

    def is_searchable(self):
        return self.is_visible

    def get_num_delegates(self):
        return self.committeeassignment_set.aggregate(
            total_delegates=models.Sum('num_delegates'))['total_delegates']

    def get_awards(self):
        awards = self.awards.order_by('award__name')
        # Move outstanding delegate to after best delegate
        # Should be fixed properly in the future (new field on Award)
        awards = [award for award in awards]
        outstanding = awards.pop()
        awards.insert(1, outstanding)
        return awards


class CommitteeApplication(models.Model):
    """
    An abstract base class used by all committee applications
    """
    class Meta:
        abstract = True

    name = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    head_delegate_name = models.CharField(max_length=100, verbose_name="Name of head delegate")
    field_of_study = models.CharField(max_length=100)
    previous_mun_experience = models.TextField(verbose_name="Describe your previous Model UN experience.")

    def __unicode__(self):
        return '%s from %s' % (self.name, self.school)


class NcaaApplication(CommitteeApplication):
    class Meta:
        verbose_name = 'Committee application: NCAA'
        verbose_name_plural = 'Committee applications: NCAA'

    why_you = models.TextField(verbose_name='Why do you want to be part of the NCAA committee? What do you think you can add to the simulation?')
    sports = models.TextField(verbose_name='What do you think is the biggest problem facing college sports and how do you think this problem should be tackled?')
    favorite_sport = models.TextField(verbose_name='What is your favourite sport and why this is the case?')
    regulation = models.TextField(verbose_name='Describe in less than 300 words what roles the NCAA should play in regulating collegiate sports in the USA. ')


class NintendoApplication(CommitteeApplication):
    class Meta:
        verbose_name = 'Committee application: Nintendo'
        verbose_name_plural = 'Committee applications: Nintendo'

    why_apply = models.TextField(verbose_name='Why have you decided to apply for this committee?')
    why_you = models.TextField(verbose_name='Why should you be part of the Delegate\'s Choice Committee? What skills do you have that would be applicable to help lead Nintendo into a new direction?')
    character = models.TextField(verbose_name='Name a Nintendo character you would be and explain why?')
    situation = models.TextField(verbose_name='Describe a situation where you thought "out of the box" to solve a problem?')
    company = models.TextField(verbose_name='Describe how you think Nintendo is as a company and what it needs to do to compete in the current marketplace:')


class CriminalCourtApplication(CommitteeApplication):
    class Meta:
        verbose_name = 'Committee application: ICC'
        verbose_name_plural = 'Committee applications: ICC'

    why_you = models.TextField(verbose_name='Why should you be part of the International Criminal Court committee? What skills do you have that would be applicable to trial simulation? ')
    libyan = models.TextField(verbose_name='What is your level of interest and knowledge in the 2011 Libyan Civil War?')
    meal = models.TextField(verbose_name='Name a world leader that you would like to have a meal with and why? ')
    alfred = models.TextField(verbose_name='In your own opinion, in 300 words or less, if Alfred murders Bill through means provided to Alfred by Claire, should Claire be prosecuted?')


class EnronApplication(CommitteeApplication):
    class Meta:
        verbose_name = 'Committee application: Enron Crisis'
        verbose_name_plural = 'Committee applications: Enron Crisis'

    interest = models.TextField(verbose_name='What interests you in the Enron Scandal? And what knowledge do you possess in economic/financial/political backgrounds?')
    who = models.TextField(verbose_name='Who do you think played the most important role in causing the crisis, and who played the most important role in its resolution?')
    state = models.TextField(verbose_name='What US state did Enron increase the electricity prices in?')
    precedent = models.TextField(verbose_name='In 300 words or less, please explain how the Enron Crisis set precedent for the 2008 financial crisis.')


class AdHocApplication(CommitteeApplication):
    class Meta:
        verbose_name = 'Committee application: Ad-hoc'
        verbose_name_plural = 'Committee applications: Ad-hoc'

    strategy = models.TextField(verbose_name='Outline your strategy for winning an Ad-Hoc crisis committee.  What are your strengths and weaknesses and what will be your most significant challenge?')
    ngo_or_corp = models.TextField(verbose_name='Would you rather manage an NGO in a rural developing region or climb a corporate ladder in New York City?')
    leader = models.TextField(verbose_name='Choose an active American politician, businessperson, or leader and explain why you embody them.')
    america = models.TextField(verbose_name='Describe in 300 words or less what is wrong with America.')


class CommitteeAssignment(models.Model):
    class Meta:
        ordering = ('school', 'committee')
        permissions = (("can_view_papers", "Can view position papers"),)

    # Number of delegates is usually 1, except in double-delegation committees
    school = models.ForeignKey('mcmun.RegisteredSchool')
    num_delegates = models.IntegerField(default=1)
    committee = models.ForeignKey(Committee, limit_choices_to={
        'is_assignable': True,
    })
    # The country or character name, in plain text
    assignment = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    position_paper = models.FileField(upload_to=get_position_paper_path, blank=True, null=True)
    is_voting = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s in %s" % (self.assignment, self.committee)

    def is_filled(self):
        return self.delegateassignment_set.filter(delegate_name__isnull=False).count() == self.num_delegates


class DelegateAssignment(models.Model):
    class Meta:
        unique_together = ('committee_assignment', 'delegate_name')

    committee_assignment = models.ForeignKey(CommitteeAssignment)
    # Blank until a delegate is there
    delegate_name = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        if self.delegate_name:
            return self.delegate_name
        else:
            return "N/A"


class Award(models.Model):
    name = models.CharField(max_length=50)
    committees = models.ManyToManyField(Committee, limit_choices_to={
        'is_assignable': True,
    })

    def __unicode__(self):
        return self.name


class AwardAssignment(models.Model):
    award = models.ForeignKey(Award, related_name='assignments')
    committee = models.ForeignKey(Committee, related_name='awards')
    position = models.ForeignKey(CommitteeAssignment, null=True, blank=True)

    def __unicode__(self):
        return "%s in %s - %s" % (self.award, self.committee.name, self.position)


def create_delegate_assignments(sender, instance, created, **kwargs):
    """
    Defines a post_save hook to create the right number of DelegateAssignments
    (with no delegate name specified) for each CommitteeAssignment
    """
    if created:
        for i in xrange(instance.num_delegates):
            instance.delegateassignment_set.create()

models.signals.post_save.connect(create_delegate_assignments,
    sender=CommitteeAssignment)


def update_award_assignments(sender, instance, action, reverse, *args,
    **kwargs):
    """
    Defines an m2m_changed hook to create/remove AwardAssignments as necessary
    when the list valid committees for an Award is updated.
    """
    if not reverse:
        if action == 'post_add':
            for committee in instance.committees.all():
                instance.assignments.get_or_create(committee=committee)
        elif action == 'pre_clear':
            instance.assignments.all().delete()

models.signals.m2m_changed.connect(update_award_assignments,
    sender=Award.committees.through)

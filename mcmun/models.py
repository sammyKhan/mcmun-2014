# coding: utf-8

from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver

from mcmun.utils import generate_random_password
from mcmun.constants import MIN_NUM_DELEGATES, MAX_NUM_DELEGATES, COUNTRIES, \
                            DELEGATION_FEE, PUB_CRAWL_COST
from mcmun.tasks import send_email, generate_invoice
from committees.models import Committee, DelegateAssignment


class RegisteredSchool(models.Model):
    class Meta:
        ordering = ['school_name']

    school_name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=2, choices=COUNTRIES)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)

    num_delegates = models.IntegerField(default=1, choices=[(n, n) for n in xrange(MIN_NUM_DELEGATES, MAX_NUM_DELEGATES + 1)])
    use_online_payment = models.BooleanField()
    use_tiered = models.BooleanField(default=False)
    use_priority = models.BooleanField(default=False)
    match_prefs = (
            ('N', 'No Thanks'),
            ('F', 'Match me with other Females'),
            ('M', 'Match me with other Males'),
    )
    single_delegate = models.CharField(max_length=1, choices=match_prefs, default='N')
    want_mobile_app = models.BooleanField(default=False, verbose_name="Would you be interested in substituting your printed delegate handbook with an integrated mobile app? (iOS and Android)")

    amount_paid = models.DecimalField(default=Decimal(0), max_digits=6, decimal_places=2)

    num_pub_crawl = models.IntegerField(default=0, verbose_name="Number of delegates interested in attending Pub Crawl (cost: $15.50 per delegate)")
    num_non_alcohol = models.IntegerField(default=0, verbose_name="Number of delegates who would prefer to attend a non-alcoholic event instead")
    pub_crawl_final = models.BooleanField(default=False)

    # This should really have been a OneToOneField. Too late now. Next year.
    # Only set iff the user has been approved
    account = models.ForeignKey(User, null=True)
    # Needs a boolean field anyway to make the admin interface better
    is_approved = models.BooleanField(default=False, verbose_name="Approve school")
    # Effective only for schools that have registered after Sept 1 (when this was deployed)
    pays_convenience_fee = models.BooleanField(default=False, editable=False)

    # Committee preferences. SO BAD
    committee_1 = models.ForeignKey(Committee, blank=True, null=True, related_name="school_1")
    committee_2 = models.ForeignKey(Committee, blank=True, null=True, related_name="school_2")
    committee_3 = models.ForeignKey(Committee, blank=True, null=True, related_name="school_3")
    committee_4 = models.ForeignKey(Committee, blank=True, null=True, related_name="school_4")
    committee_5 = models.ForeignKey(Committee, blank=True, null=True, related_name="school_5")

    merch_order_final = models.BooleanField(default=False)

    def has_prefs(self):
        return (self.committee_1 or self.committee_2 or self.committee_3 or
            self.committee_4 or self.committee_5)

    def is_international(self):
        """
        Checks if the institution is "international" (i.e. outside North America).
        """
        return self.country != 'CA' and self.country != 'US'

    def get_payment_type(self):
        if self.is_international():
            payment_type = 'international'
        elif self.use_priority:
            payment_type = 'priority'
        else:
            payment_type = 'regular'

        return payment_type

    def get_currency(self):
        """
        Returns CAD if the institution is Canadian, USD otherwise.
        """
        return 'CAD' if self.country == 'CA' else 'USD'

    # These are messy. Deal with it another time.
    def get_total_convenience_fee(self):
        return "%.2f" % ((self.num_delegates * self.get_delegate_fee() + DELEGATION_FEE) * 0.03)

    def get_deposit_convenience_fee(self):
        return "%.2f" % ((DELEGATION_FEE + (self.get_delegate_fee() * self.num_delegates) * 0.5) * 0.03)

    def get_remainder_convenience_fee(self):
        return "%.2f" % ((self.get_delegate_fee() * self.num_delegates * 0.5) * 0.03)

    def add_convenience_fee(self, number):
        """
        Incorporates a 3% convenience fee into the number given iff the school
        has selected online payment and has registered after Sept 1.
        """
        if self.use_online_payment and self.pays_convenience_fee:
            return number * 1.03
        else:
            return number

    def get_delegate_fee(self):
        if self.is_international():
            delegate_fee = 60
        else:
            delegate_fee = 85 if self.use_priority else 95

        return delegate_fee

    def get_total_delegate_fee(self):
        return self.get_delegate_fee() * self.num_delegates

    def get_total_owed(self):
        total_owed = self.num_delegates * self.get_delegate_fee() + DELEGATION_FEE

        return "%.2f" % self.add_convenience_fee(total_owed)

    def get_deposit(self):
        deposit = DELEGATION_FEE + (self.get_delegate_fee() * self.num_delegates) * 0.5

        return "%.2f" % self.add_convenience_fee(deposit)

    def get_remainder(self):
        remainder = self.get_delegate_fee() * self.num_delegates * 0.5

        return "%.2f" % self.add_convenience_fee(remainder)

    def amount_owed(self):
        if self.use_tiered:
            return "$%s ($%s deposit, $%s remainder)" % (self.get_total_owed(), self.get_deposit(), self.get_remainder())
        else:
            return "$%s" % self.get_total_owed()

    def send_success_email(self):
        # Send out email to user (receipt of registration)
        receipt_subject = 'Successful registration for McMUN 2015'
        receipt_message_filename = 'registration_success'
        receipt_context = {
            'first_name': self.first_name,
            'school_name': self.school_name,
        }

        send_email.delay(receipt_subject, receipt_message_filename, [self.email], context=receipt_context)

        # Send email to Charge, finance, me (link to approve registration)
        approve_subject = 'New registration for McMUN'
        approve_message_filename = 'registration_approve'
        approve_context = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'school_name': self.school_name,
            'email': self.email,
            'admin_url': settings.ADMIN_URL,
            'school_id': self.id,
        }

        send_email.delay(approve_subject, approve_message_filename, [settings.IT_EMAIL, settings.CHARGE_EMAIL], context=approve_context)

    def send_invoice_email(self, username, password):
        print "about to delay the generate_invoice task"
        generate_invoice.delay(self.id, username, password)

    def finalise_pub_crawl(self):
        self.pub_crawl_final = True
        self.save()

        if self.num_pub_crawl > 0 :
            # Send an email containing the invoice (just in the email body)
            subject = 'Invoice for McMUN 2015 Pub Crawl registration'
            filename = 'pub_crawl'
            context = {
                'first_name': self.first_name,
                'num_delegates': self.num_pub_crawl,
                'cost_per_delegate': PUB_CRAWL_COST,
                'total_cost': self.get_pub_crawl_total_owed(),
            }

            send_email.delay(subject, filename, [self.email], context=context,
                             bcc=[settings.IT_EMAIL, settings.CHARGE_EMAIL,
                                  settings.FINANCE_EMAIL])

    def has_unfilled_assignments(self):
        return any(not c.is_filled() for c in self.committeeassignment_set.all())

    def get_merch_total_owed(self):
        item_orders = self.itemorder_set.filter(bundle_order__isnull=True)
        bundle_orders = self.bundleorder_set.all()
        total_cost = 0

        for item_order in item_orders:
            total_cost += item_order.quantity * item_order.item.online_price

        for bundle_order in bundle_orders:
            total_cost += bundle_order.quantity * bundle_order.bundle.online_price

        return total_cost

    def get_num_assignments(self):
        DelegateAssignment = models.loading.get_model('committees',
            'DelegateAssignment')
        return DelegateAssignment.objects.filter(
            committee_assignment__school=self).count()

    def get_pub_crawl_total_owed(self):
        return "$%.2f" % (PUB_CRAWL_COST * self.num_pub_crawl)

    def __unicode__(self):
        return self.school_name


class ScholarshipApp(models.Model):
    school = models.OneToOneField(RegisteredSchool)
    club_name = models.CharField(max_length=100)
    num_days_staying = models.IntegerField()
    previously_attended = models.BooleanField()
    previous_scholarship_amount = models.IntegerField(null=True, blank=True)
    previous_scholarship_year = models.IntegerField(null=True, blank=True)
    impact_on_delegation = models.TextField()
    principles_of_organisation = models.TextField()
    importance_of_mcmun = models.TextField()
    how_funding_works = models.TextField()
    other_funding_sources = models.TextField()
    budget = models.TextField()
    other_information = models.TextField(null=True, blank=True)
    co_head_name = models.CharField(max_length=100, null=True, blank=True)
    co_head_email = models.EmailField(max_length=255, null=True, blank=True)
    co_head_phone = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.school.school_name


"""
Just an abstract base class to avoid having to type all this out twice
(I'll add a Coordinator model soon)
"""
class OrganisingMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    slug = models.SlugField()

    class Meta:
        abstract = True


class SecretariatMember(OrganisingMember):
    email = models.CharField(max_length=100, help_text="Just the part that goes before @mcmun.org")

    def __unicode__(self):
        return u'%s – %s' % (self.name, self.position)

    def get_absolute_url(self):
        return '/secretariat#%s' % self.slug


class Coordinator(OrganisingMember):
    def __unicode__(self):
        return self.name


class ScheduleItem(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_visible = models.BooleanField(default=False)


@receiver(models.signals.pre_save, sender=RegisteredSchool, dispatch_uid="approve_schools")
def approve_schools(sender, instance, **kwargs):
    """
    When a school is approved, create an account for it (with a random
    password) and send an email containing the login info as well as the
    invoice (attached as a PDF).
    """
    if instance.is_approved and instance.account is None:
        # School does not have an account. Make one!
        password = generate_random_password()
        username = instance.email[:30]
        new_account = User.objects.create_user(username=username,
                                               password=password)
        instance.account = new_account

        instance.send_invoice_email(new_account.username, password)

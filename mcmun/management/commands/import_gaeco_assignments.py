import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from committees.models import Committee, CommitteeAssignment
from mcmun.models import RegisteredSchool


class Command(BaseCommand):
    help = ("Imports stuff")

    def handle(self, filepath, **options):
        # Get all the committees, by slug
        committees = {}
        for committee in Committee.objects.all():
            committees[committee.slug] = committee

        file = open(filepath)
        reader = csv.reader(file, quotechar='"')
        next(reader)
        for row in reader:
            country = row[0]

            # Strip the * at the end if there is one (means non-voting)
            is_voting = True
            if country.endswith('*'):
                country = country[:-1]
                is_voting = False

            columns = ['specpol', 'legal', 'unesco', 'iaea', 'cnd', 'wto', 'unsc']
            school_name = unicode(row[8], 'utf-8')
            if school_name == "":
                continue
            try:
                school = RegisteredSchool.objects.get(school_name=school_name)
                for i, committee_slug in enumerate(columns):
                    committee = committees[committee_slug]
                    num_cell = row[i + 1]

                    if num_cell != "0" or len(num_cell) == 0:
                        # Create the committee assignment
                        num_delegates = int(num_cell[0])
                        school.committeeassignment_set.create(
                            committee=committee,
                            assignment=country,
                            num_delegates=num_delegates,
                            is_voting=is_voting,
                        )
            except RegisteredSchool.DoesNotExist:
                print(school_name)
            except Error, e:
                print(e)

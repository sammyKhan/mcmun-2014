import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from committees.models import Committee, CommitteeAssignment
from mcmun.models import RegisteredSchool


class Command(BaseCommand):
    help = ("Imports stuff")

    def handle(self, **options):
        filepath = raw_input("CSV file to import: ")
        try:
            file = open(filepath)
            reader = csv.reader(file, quotechar='"')
        except:
            print("Bad file.")
            return

        slug = raw_input("Slug of the committee to assign: ")
        try:
            committee = Committee.objects.get(slug=slug)
        except:
            print("Bad slug.")
            return

        for row in reader:
            position = row[0]
            school = row[1]

            try:
                school = RegisteredSchool.objects.get(school_name=school)
                school.committeeassignment_set.create(
                    committee=committee,
                    assignment=position,
                    num_delegates=1
                )
            except RegisteredSchool.DoesNotExist:
                print(school)

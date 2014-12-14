from django.core.management.base import BaseCommand, CommandError
from mcmun.models import RegisteredSchool

from django_xhtml2pdf.utils import generate_pdf

class Command(BaseCommand):
    def handle(self, *args, **options):
        help = 'Generate a custom invoice'

        pk = raw_input('Enter the primary key of the school: ')
        try:
            school = RegisteredSchool.objects.get(pk=pk)
        except RegisteredSchool.DoesNotExist:
           raise CommandError('School with ID %s does not exist!' % pk)

        confirm = raw_input('School found: %s. Type y to confirm: ' % school)
        if confirm != 'y':
            self.stdout.write('Regeneration cancelled.')
            return

        invoice_id = 'MC15' + str(pk).zfill(3) + 'X'

        num_delegates = int(raw_input('Number of delegates to include: '))

        school.num_delegates = num_delegates
        school.use_tiered = False
        use_priority = raw_input('Use priority? ') == "y"
        school.use_priority = use_priority

        pdf_context = {
            'invoice_id': invoice_id,
            'payment_type': school.get_payment_type(),
            'school': school,
        }

        # Generate the invoice PDF, save it under tmp/
        pdf_filename = 'tmp/mcmun_invoice_%s.pdf' % invoice_id
        file = open(pdf_filename, 'wb')
        pdf = generate_pdf('pdf/invoice.html', file_object=file, context=pdf_context)
        file.close()


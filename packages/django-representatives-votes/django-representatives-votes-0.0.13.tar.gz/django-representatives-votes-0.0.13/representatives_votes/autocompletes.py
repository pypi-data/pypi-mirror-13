from dal import autocomplete

from django.db.models import Q

from models import Proposal


class ProposalAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Proposal.objects.all()

        if self.q:
            qs = qs.filter(
                Q(dossier__title__icontains=self.q) |
                Q(title__icontains=self.q) |
                Q(reference__icontains=self.q)
            )

        return qs

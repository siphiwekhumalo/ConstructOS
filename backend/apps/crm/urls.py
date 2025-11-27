from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, ContactViewSet, AddressViewSet, PipelineStageViewSet,
    LeadViewSet, OpportunityViewSet, CampaignViewSet, MailingListViewSet,
    SegmentViewSet, SlaViewSet, TicketViewSet, TicketCommentViewSet, ClientViewSet
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'pipeline-stages', PipelineStageViewSet)
router.register(r'leads', LeadViewSet)
router.register(r'opportunities', OpportunityViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'mailing-lists', MailingListViewSet)
router.register(r'segments', SegmentViewSet)
router.register(r'slas', SlaViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'ticket-comments', TicketCommentViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

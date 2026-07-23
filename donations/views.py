from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from .models import DonationListing, MatchRequest, DonationImage
from .serializers import (
    DonationListingSerializer, DonationListingListSerializer,
    MatchRequestSerializer, MatchRequestListSerializer,
    DonationImageSerializer, UserSerializer, DonorProfileSerializer,
    RecipientProfileSerializer
)
from accounts.models import CustomUser
from donors.models import DonorProfile
from recipients.models import RecipientProfile
from .cache import cache_result, cache_queryset, generate_cache_key, invalidate_cache_pattern
from django.views.generic import ListView
import hashlib
import json
from functools import wraps




class IsDonorOrReadOnly:
    """Custom permission to only allow donors to edit their own donations"""
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated

        # Write permissions are only allowed to the donor
        return obj.donor == request.user


class IsRecipientOrReadOnly:
    """Custom permission to only allow recipients to edit their own requests"""
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated

        # Write permissions are only allowed to the recipient
        return obj.recipient == request.user


class IsDonorOfObject:
    """Custom permission to only allow donors of a specific object to edit it"""
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated

        # Write permissions are only allowed to the donor of the object
        if hasattr(obj, 'donor'):
            return obj.donor == request.user
        elif hasattr(obj, 'donation'):
            return obj.donation.donor == request.user

        return False


class DonationListingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing donation listings"""
    queryset = DonationListing.objects.all().select_related(
        'donor', 'donor_profile'
    ).prefetch_related('images')
    serializer_class = DonationListingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'food_type', 'donor']
    search_fields = ['description', 'food_type', 'pickup_location']
    ordering_fields = ['created_at', 'expiry_date', 'pickup_window_start']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return DonationListingListSerializer
        return DonationListingSerializer

    def get_queryset(self):
        """Filter queryset based on user role and query parameters with caching."""
        # Create a cache key based on the request parameters and user
        user = self.request.user
        query_params = self.request.query_params.dict()

        # Create a cache key that includes user info and query parameters
        cache_key_data = {
            'user_id': user.id if user.is_authenticated else None,
            'user_role': user.role if user.is_authenticated else 'anonymous',
            'query_params': query_params
        }
        cache_key = generate_cache_key('donation_list', **cache_key_data)

        # Try to get cached queryset (evaluated as list)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # If not in cache, build queryset
        queryset = DonationListing.objects.all().select_related(
            'donor', 'donor_profile'
        ).prefetch_related('images')

        # Filter by availability if requested
        available_only = query_params.get('available_only', None)
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(
                status='available'
            ).exclude(
                expiry_date__lt=timezone.now()
            )

        # Filter by expiring soon
        expiring_soon = query_params.get('expiring_soon', None)
        if expiring_soon and expiring_soon.lower() == 'true':
            from datetime import timedelta
            expiry_threshold = timezone.now() + timedelta(hours=24)
            queryset = queryset.filter(
                status='available',
                expiry_date__lte=expiry_threshold,
                expiry_date__gt=timezone.now()
            )

        # Filter by user's own donations
        my_donations = query_params.get('my_donations', None)
        if my_donations and my_donations.lower() == 'true':
            queryset = queryset.filter(donor=user)

        # Filter by recipient's requests (for recipients to see what they've requested)
        my_requests = query_params.get('my_requests', None)
        if my_requests and my_requests.lower() == 'true' and user.role == 'recipient':
            from donations.models import MatchRequest
            requested_donation_ids = MatchRequest.objects.filter(
                recipient=user
            ).values_list('donation_id', flat=True)
            queryset = queryset.filter(id__in=requested_donation_ids)

        # Apply filtering, searching, and ordering from filter_backends
        # Note: We apply these after caching the base queryset to allow for
        # different filter combinations while still benefiting from caching
        # the expensive joins

        # For now, we'll cache the base queryset and apply filters dynamically
        # In a more advanced implementation, we might cache per filter combination

        # Apply backend filters (DjangoFilterBackend, SearchFilter, OrderingFilter)
        # We need to apply these to our queryset
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        # Cache the result (evaluate queryset to list for caching)
        result = list(queryset)
        cache.set(cache_key, result, 300)  # Cache for 5 minutes

        return result

    def perform_create(self, serializer):
        """Set the donor to the current user when creating a donation"""
        serializer.save(donor=self.request.user)
        self.invalidate_related_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.invalidate_related_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_related_cache()

    def invalidate_related_cache(self):
        """Invalidate cache for donation listings and stats"""
        # Invalidate donation list cache (we'll use a pattern-based invalidation)
        # Since we don't have a simple pattern, we'll clear the cache for donation_list and donation_stats
        # In a production setup, we would use a more sophisticated cache invalidation strategy
        # For now, we'll clear the entire cache (which is not ideal but safe)
        # TODO: Implement proper cache key tracking for invalidation
        try:
            # Try to delete pattern if using redis
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern('donation_list:*')
                cache.delete_pattern('donation_stats:*')
            else:
                # Fallback: clear cache (not ideal but safe)
                cache.clear()
        except Exception:
            cache.clear()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def claim(self, request, pk=None):
        """Claim a donation"""
        donation = self.get_object()
        user = request.user

        # Check if user is a recipient
        if user.role != 'recipient':
            return Response(
                {'error': 'Only recipients can claim donations'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            donation.claim(user)
            return Response(
                {'status': 'Donation claimed successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsDonorOfObject])
    def cancel(self, request, pk=None):
        """Cancel a donation"""
        donation = self.get_object()
        try:
            donation.cancel()
            return Response(
                {'status': 'Donation cancelled successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsDonorOfObject])
    def complete(self, request, pk=None):
        """Mark donation as completed"""
        donation = self.get_object()
        try:
            donation.complete()
            return Response(
                {'status': 'Donation marked as completed'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get donation statistics with caching."""
        user = request.user
        if user.is_authenticated:
            cache_key = generate_cache_key('donation_stats', user.id, user.role)
        else:
            cache_key = generate_cache_key('donation_stats_anonymous')

        # Try to get cached stats
        cached_stats = cache.get(cache_key)
        if cached_stats is not None:
            return Response(cached_stats)

        # If not in cache, compute stats
        if user.role == 'donor':
            # Donor stats
            donations = DonationListing.objects.filter(donor=user)
            stats = {
                'total_donations': donations.count(),
                'available_donations': donations.filter(status='available').count(),
                'claimed_donations': donations.filter(status__in=['claimed', 'pending', 'matched']).count(),
                'completed_donations': donations.filter(status='completed').count(),
                'cancelled_donations': donations.filter(status='cancelled').count(),
            }
        elif user.role == 'recipient':
            # Recipient stats
            from donations.models import MatchRequest
            requests = MatchRequest.objects.filter(recipient=user)
            stats = {
                'total_requests': requests.count(),
                'pending_requests': requests.filter(status='pending').count(),
                'accepted_requests': requests.filter(status='accepted').count(),
                'completed_requests': requests.filter(status='completed').count(),
                'cancelled_requests': requests.filter(status='cancelled').count(),
                'rejected_requests': requests.filter(status='rejected').count(),
            }
        else:
            # Admin or general stats
            stats = {
                'total_donations': DonationListing.objects.count(),
                'available_donations': DonationListing.objects.filter(status='available').count(),
                'total_requests': MatchRequest.objects.count(),
                'completed_donations': DonationListing.objects.filter(status='completed').count(),
            }

        # Cache the stats for 5 minutes
        cache.set(cache_key, stats, 300)

        return Response(stats)


class MatchRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing match requests"""
    queryset = MatchRequest.objects.all().select_related(
        'donation', 'donation__donor', 'recipient', 'recipient__recipient_profile',
        'responded_by'
    )
    serializer_class = MatchRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'donation', 'recipient']
    search_fields = ['message', 'special_instructions']
    ordering_fields = ['requested_at', 'responded_at']
    ordering = ['-requested_at']

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return MatchRequestListSerializer
        return MatchRequestSerializer

    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user

        # Users can only see their own requests/donations unless they're admin
        if user.role == 'donor':
            # Donors see requests for their donations
            queryset = queryset.filter(donation__donor=user)
        elif user.role == 'recipient':
            # Recipients see their own requests
            queryset = queryset.filter(recipient=user)
        # Admins see everything (no filter)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsDonorOfObject])
    def accept(self, request, pk=None):
        """Accept a request"""
        request_obj = self.get_object()
        response_message = request.data.get('response_message', '')
        try:
            request_obj.accept(request.user, response_message)
            return Response(
                {'status': 'Request accepted successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsDonorOfObject])
    def reject(self, request, pk=None):
        """Reject a request"""
        request_obj = self.get_object()
        response_message = request.data.get('response_message', '')
        try:
            request_obj.reject(request.user, response_message)
            return Response(
                {'status': 'Request rejected successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsDonorOfObject])
    def complete(self, request, pk=None):
        """Mark request as completed"""
        request_obj = self.get_object()
        try:
            request_obj.complete(request.user)
            return Response(
                {'status': 'Request marked as completed'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsDonorOfObject | IsRecipientOrReadOnly])
    def cancel(self, request, pk=None):
        """Cancel a request"""
        request_obj = self.get_object()
        user = request.user
        try:
            request_obj.cancel(user)
            return Response(
                {'status': 'Request cancelled successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Set the recipient to the current user when creating a request"""
        serializer.save(recipient=self.request.user)
        self.invalidate_related_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.invalidate_related_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_related_cache()

    def invalidate_related_cache(self):
        """Invalidate cache for match requests and related stats"""
        try:
            # Try to delete pattern if using redis
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern('match_request:*')
                cache.delete_pattern('match_request_stats:*')
            else:
                # Fallback: clear cache (not ideal but safe)
                cache.clear()
        except Exception:
            cache.clear()


class DonationImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing donation images"""
    queryset = DonationImage.objects.all().select_related(
        'donation', 'uploaded_by'
    )
    serializer_class = DonationImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['donation', 'is_primary']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # Users can only see images for their own donations
        if user.role == 'donor':
            queryset = queryset.filter(donation__donor=user)
        elif user.role == 'recipient':
            # Recipients can see images for donations they've requested or that are available
            from donations.models import MatchRequest
            requested_donation_ids = MatchRequest.objects.filter(
                recipient=user, status__in=['pending', 'accepted', 'completed']
            ).values_list('donation_id', flat=True)
            available_donation_ids = DonationListing.objects.filter(
                status='available'
            ).values_list('id', flat=True)
            accessible_donation_ids = set(list(requested_donation_ids) + list(available_donation_ids))
            queryset = queryset.filter(donation_id__in=accessible_donation_ids)
        # Admins see everything

        return queryset

    def perform_create(self, serializer):
        """Set the uploaded_by to the current user when creating an image"""
        serializer.save(uploaded_by=self.request.user)
        self.invalidate_related_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.invalidate_related_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_related_cache()

    def invalidate_related_cache(self):
        """Invalidate cache for donation images and related stats"""
        try:
            # Try to delete pattern if using redis
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern('donation_image:*')
                cache.delete_pattern('donation_image_stats:*')
            else:
                # Fallback: clear cache (not ideal but safe)
                cache.clear()
        except Exception:
            cache.clear()


class DonationListView(ListView):
    """View for listing all available donations"""
    model = DonationListing
    template_name = 'donations/donation_list.html'
    context_object_name = 'donations'
    paginate_by = 12

    def get_queryset(self):
        """Return only available donations that haven't expired"""
        return DonationListing.objects.filter(
            status='available'
        ).exclude(
            expiry_date__lt=timezone.now()
        ).select_related('donor', 'donor_profile').prefetch_related('images').order_by('-created_at')
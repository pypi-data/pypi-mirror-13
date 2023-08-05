from mongoengine import ValidationError
from mongoengine.queryset.base import BaseQuerySet
from rest_framework import generics as drf_generics
from rest_framework import mixins


class GenericAPIView(drf_generics.GenericAPIView):
    """ Adaptation of DRF GenericAPIView """
    lookup_field = 'id'

    def get_queryset(self):
        ""
        queryset = super(GenericAPIView, self).get_queryset()

        if isinstance(queryset, BaseQuerySet):
            queryset = queryset.all()

        return queryset

    def get_object(self):
        ""
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        try:
            obj = queryset.get(**filter_kwargs)
        except (queryset._document.DoesNotExist, ValidationError):
            from django.http import Http404
            raise Http404('No %s matches the given query.' % queryset._document._class_name)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class CreateAPIView(mixins.CreateModelMixin,
                    GenericAPIView):
    "Adaptation of DRF CreateAPIView"
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    "Adaptation of DRF ListAPIView"
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):
    "Adaptation of DRF ListCreateAPIView"
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin,
                    GenericAPIView):
    "Adaptation of DRF UpdateAPIView"
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericAPIView):
    "Adaptation of DRF RetrieveUpdateAPIView"
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericAPIView):
    "Adaptation of DRF RetrieveDestroyAPIView"
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   GenericAPIView):
    "Adaptation of DRF RetrieveUpdateDestroyAPIView"
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Partner, Images, PartnerProduct, ProductCategory


class PartnerSerializer(serializers.ModelSerializer):
    is_partner_available = serializers.SerializerMethodField()

    class Meta:
        model = Partner()
        fields = "__all__"

    def get_is_partner_available(self, obj):
        return obj.is_partner_available()


class PartnerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["partner"] = PartnerSerializer(read_only=True)
        return super(PartnerUserSerializer, self).to_representation(instance)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = "__all__"


class PartnerProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerProduct
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["category"] = ProductCategorySerializer(read_only=True)
        return super(PartnerProductSerializer, self).to_representation(instance)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"

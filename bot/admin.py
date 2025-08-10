from django.contrib import admin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    TgUser, TgGroup, GroupAdmin, BlockedWord, TgInviterUser,
    ChannelMember, Advertisement, AdvertisementHistory
)

# Default User modelini qayta ro'yxatdan chiqarib, custom admin
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy maʼlumotlar', {'fields': ('first_name', 'last_name', 'email')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )
    list_per_page = 25


@admin.register(TgUser)
class TgUserAdmin(ModelAdmin):
    list_display = ('chat_id', 'full_name', 'created_at', 'updated_at', 'is_admin')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('chat_id', 'full_name')
    ordering = ('-created_at',)
    list_per_page = 30


class GroupAdminInline(TabularInline):
    model = GroupAdmin
    extra = 0
    readonly_fields = ('user_chat_id', 'user_full_name')


@admin.register(TgGroup)
class TgGroupAdmin(ModelAdmin):
    list_display = ('title', 'chat_id', 'invite_count', 'required_channel_username', 'is_admin', 'created_at')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('title', 'chat_id')
    ordering = ('-created_at',)
    readonly_fields = ('chat_id',)
    inlines = [GroupAdminInline]
    list_per_page = 25


@admin.register(GroupAdmin)
class GroupAdminAdmin(ModelAdmin):
    list_display = ("user_full_name", "tg_group", "user_chat_id")
    list_filter = ("tg_group",)
    search_fields = ("user_full_name", "user_chat_id", "tg_group__title", "tg_group__chat_id")
    ordering = ("tg_group", "user_full_name")
    readonly_fields = ("tg_group", "user_chat_id")
    list_per_page = 25


@admin.register(BlockedWord)
class BlockedWordAdmin(ModelAdmin):
    list_display = ('word', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 30


@admin.register(TgInviterUser)
class TgInviterUserAdmin(ModelAdmin):
    list_display = (
        "tg_group", "inviter_full_name", "inviter_chat_id",
        "invite_count", "last_invite_at", "is_allow",
        "created_at", "updated_at"
    )
    list_filter = ("tg_group", "is_allow", "created_at")
    search_fields = ("inviter_full_name", "inviter_chat_id")
    ordering = ("-invite_count", "-last_invite_at")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 30


@admin.register(ChannelMember)
class ChannelMemberAdmin(ModelAdmin):
    list_display = ("full_name", "user_chat_id", "channel_id", "joined_at")
    search_fields = ("full_name", "user_chat_id", "channel_id")
    list_filter = ("channel_id",)
    ordering = ("-joined_at",)
    readonly_fields = ("joined_at",)
    list_per_page = 30


class AdvertisementHistoryInline(TabularInline):
    model = AdvertisementHistory
    extra = 0
    readonly_fields = ("chat_id", "title", "is_success", "description")
    can_delete = False
    show_change_link = False


@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    list_display = (
        "id", "forward_from_chat_id", "forward_message_id",
        "target_type", "created_by", "created_at", "is_sent",
        "success", "error"
    )
    list_filter = ("target_type", "is_sent", "created_at")
    search_fields = ("created_by",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "success", "error")
    inlines = [AdvertisementHistoryInline]
    list_per_page = 25


@admin.register(AdvertisementHistory)
class AdvertisementHistoryAdmin(ModelAdmin):
    list_display = ("advertisement", "chat_id", "title", "is_success", "description")
    list_filter = ("is_success",)
    search_fields = ("title", "chat_id")
    ordering = ("-advertisement",)
    list_per_page = 30

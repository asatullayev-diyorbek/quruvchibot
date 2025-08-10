from django.contrib import admin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, TabularInline
from bot.models import TgGroup, GroupAdmin, BlockedWord, TgUser, TgInviterUser, ChannelMember, Advertisement, \
    AdvertisementHistory

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
    list_display = ('chat_id', 'full_name', 'created_at', 'updated_at')
    search_fields = ('chat_id', 'full_name', 'created_at')
    list_filter = ('chat_id', 'full_name', 'created_at')
    list_per_page = 30

class GroupAdminInline(TabularInline):
    model = GroupAdmin
    extra = 0
    list_display = ("user_full_name", "user_chat_id")
    readonly_fields = ('user_chat_id', )


@admin.register(TgGroup)
class TgGroupAdmin(ModelAdmin):
    list_display = ('title', 'chat_id', 'is_admin', 'created_at', 'updated_at')
    list_filter = ('is_admin', 'created_at', 'updated_at')
    search_fields = ('title', 'chat_id')
    ordering = ('-created_at',)
    readonly_fields = ('chat_id', )
    list_per_page = 25

    inlines = [GroupAdminInline]


@admin.register(GroupAdmin)
class GroupAdminAdmin(ModelAdmin):
    list_display = ("user_full_name", "tg_group", "user_chat_id")
    list_filter = ("tg_group",)
    search_fields = ("user_full_name", "user_chat_id", "tg_group__title", "tg_group__chat_id")
    ordering = ("tg_group", "user_full_name")
    list_per_page = 25

    readonly_fields = ("tg_group", "user_chat_id", )

    fieldsets = (
        ("Admin haqida", {
            "fields": ("user_full_name", "user_chat_id")
        }),
        ("Guruh haqida", {
            "fields": ("tg_group",)
        }),
    )


@admin.register(BlockedWord)
class BlockedWordAdmin(ModelAdmin):
    list_display = ('word', 'created_at', 'updated_at')
    ordering = ('-created_at', )
    list_per_page = 30


@admin.register(TgInviterUser)
class TgInviterUserAdmin(ModelAdmin):
    list_display = (
        "tg_group",
        "inviter_full_name",
        "inviter_chat_id",
        "invite_count",
        "last_invite_at",
        "is_allow",
        "created_at",
        "updated_at",
    )
    list_filter = ("tg_group", "is_allow", "created_at")
    search_fields = ("inviter_full_name", "inviter_chat_id")
    ordering = ("-invite_count", "-last_invite_at")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Foydalanuvchi ma'lumotlari", {
            "fields": ("tg_group", "inviter_full_name", "inviter_chat_id")
        }),
        ("Statistika", {
            "fields": ("invite_count", "last_invite_at", "is_allow")
        }),
        ("Vaqt ma'lumotlari", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(ChannelMember)
class ChannelMemberAdmin(ModelAdmin):
    list_display = ("full_name", "user_chat_id", "channel_id", "joined_at")
    search_fields = ("full_name", "user_chat_id", "channel_id")
    list_filter = ("channel_id",)
    ordering = ("-joined_at",)
    readonly_fields = ("joined_at",)


class AdvertisementHistoryInline(TabularInline):
    model = AdvertisementHistory
    extra = 0
    readonly_fields = ("chat_id", "title", "is_success", "description")
    can_delete = True
    show_change_link = False
    per_page = 5  # faqat Django 5.0+ da ishlaydi

@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    list_display = ("id", "forward_from_chat_id", "forward_message_id", "get_target_type_display", "created_by", "created_at", "is_sent")
    list_display_links = ('id', "forward_from_chat_id", "forward_message_id", "get_target_type_display")
    list_filter = ("target_type", "is_sent", "created_at")
    search_fields = ("created_by",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    inlines = [AdvertisementHistoryInline]

    def get_target_type_display(self, obj):
        return obj.get_target_type_display()
    get_target_type_display.short_description = "Target turi"

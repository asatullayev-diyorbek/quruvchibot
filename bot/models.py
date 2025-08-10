from django.db import models


class TgUser(models.Model):
    chat_id = models.BigIntegerField(verbose_name="Chat ID")
    full_name = models.CharField(max_length=256, verbose_name="To'liq ism")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")
    is_admin = models.BooleanField(default=False, null=True, blank=True, verbose_name="Bot adminimi?")

    def __str__(self):
        return f"{self.full_name} ({self.chat_id})"

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


class TgGroup(models.Model):
    chat_id = models.BigIntegerField(verbose_name="ChatID")
    title = models.CharField(max_length=256, verbose_name="Nomi")
    invite_count = models.IntegerField(default=0, verbose_name="Majburiy a'zo qo'shish")
    required_channel = models.BigIntegerField(default=None, null=True, blank=True)
    required_channel_username = models.CharField(max_length=255, null=True, blank=True)
    required_channel_title = models.CharField(max_length=255, null=True, blank=True, default=None)
    is_admin = models.BooleanField(default=False, verbose_name="Adminmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    def __str__(self):
        return f"{self.title} ({self.chat_id})"

    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"


class GroupAdmin(models.Model):
    tg_group = models.ForeignKey(TgGroup, on_delete=models.CASCADE, verbose_name="Guruh")
    user_chat_id = models.BigIntegerField(verbose_name="Admin ChatID")
    user_full_name = models.CharField(max_length=256, verbose_name="Admin F.I.Sh")


    def __str__(self):
        return f"{self.tg_group.title} - {self.user_full_name} ({self.user_chat_id})"

    class Meta:
        verbose_name = "Guruh admini"
        verbose_name_plural = "Guruh adminlari"


class BlockedWord(models.Model):
    word = models.CharField(max_length=100, verbose_name="So'z")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = "So'z"
        verbose_name_plural = "So'zlar"


class TgInviterUser(models.Model):
    tg_group = models.ForeignKey(
        TgGroup,
        on_delete=models.CASCADE,
        verbose_name="Guruh",
        related_name="inviters"
    )
    inviter_chat_id = models.BigIntegerField(verbose_name="Qo‘shgan foydalanuvchi ChatID")
    inviter_full_name = models.CharField(max_length=256, verbose_name="Qo‘shgan foydalanuvchi F.I.Sh")

    invite_count = models.PositiveIntegerField(default=0, verbose_name="Qo‘shgan odamlar soni")
    last_invite_at = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi qo‘shgan vaqti")

    is_allow = models.BooleanField(default=False, verbose_name="Ruxsat berilganmi?")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozuv yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yozuv yangilangan vaqti")

    def __str__(self):
        return f"{self.inviter_full_name} ({self.inviter_chat_id}) - {self.invite_count} ta odam qo‘shgan"

    class Meta:
        verbose_name = "Odam qo‘shgan foydalanuvchi"
        verbose_name_plural = "Odam qo‘shgan foydalanuvchilar"
        unique_together = ("tg_group", "inviter_chat_id")


class ChannelMember(models.Model):
    channel_id = models.BigIntegerField(verbose_name="Kanal ID")
    user_chat_id = models.BigIntegerField(verbose_name="Foydalanuvchi ChatID")
    full_name = models.CharField(max_length=255)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kanal a'zosi"
        verbose_name_plural = "Kanal a'zolari"
        unique_together = ("channel_id", "user_chat_id")

    def __str__(self):
        return f"{self.full_name} ({self.user_chat_id})"

# models.py
class Advertisement(models.Model):
    TARGET_GROUPS = "groups"
    TARGET_USERS = "users"
    TARGET_CHOICES = [
        (TARGET_GROUPS, "Guruhlar"),
        (TARGET_USERS, "Foydalanuvchilar"),
    ]

    forward_from_chat_id = models.BigIntegerField(verbose_name="Forward kelgan chat ID", null=True, blank=True)
    forward_message_id = models.BigIntegerField(verbose_name="Forward kelgan xabar ID", null=True, blank=True)

    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)

    success = models.IntegerField(default=0, verbose_name="Muvaffaqqiyatli")
    error = models.IntegerField(default=0, verbose_name="Yuborilmadi")

    created_by = models.BigIntegerField(verbose_name="Admin ChatID")
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_target_type_display()} reklama ({self.created_at:%Y-%m-%d %H:%M})"


class AdvertisementHistory(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, verbose_name="Reklama")
    chat_id = models.BigIntegerField(verbose_name="ChatID")
    title = models.CharField(max_length=256, verbose_name="Nomi")
    is_success = models.BooleanField(default=False, verbose_name="Status")
    description = models.TextField(null=True, blank=True, verbose_name="Izoh / Xato sababi")

    def __str__(self):
        return f"{self.title} ({self.chat_id} - {self.advertisement}"
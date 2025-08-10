import asyncio
import aiohttp
from django.http import HttpResponse
from django.views.generic import View
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.models import Advertisement, AdvertisementHistory, TgUser, TgGroup


TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}"


class SentAdsView(View):
    async def get(self, request):
        print("📢 Reklama jo‘natish jarayoni boshlandi...")
        ads_qs = await sync_to_async(lambda: list(Advertisement.objects.filter(is_sent=False)))()
        print(f"Topildi: {len(ads_qs)} ta yuborilmagan reklama.")

        if not ads_qs:
            return HttpResponse("No pending ads")

        async with aiohttp.ClientSession() as session:
            for ad in ads_qs:
                print(f"\n▶ Reklama ID: {ad.id} | Target turi: {ad.target_type}")

                # Targetlarni olish
                if ad.target_type == Advertisement.TARGET_USERS:
                    targets = await sync_to_async(lambda: list(
                        TgUser.objects.exclude(
                            chat_id__in=AdvertisementHistory.objects.filter(advertisement=ad)
                            .values_list("chat_id", flat=True)
                        )
                    ))()
                else:
                    targets = await sync_to_async(lambda: list(
                        TgGroup.objects.exclude(
                            chat_id__in=AdvertisementHistory.objects.filter(advertisement=ad)
                            .values_list("chat_id", flat=True)
                        )
                    ))()

                print(f"🎯 Targetlar soni: {len(targets)}")

                if not targets:
                    print("❌ Targetlar topilmadi. O‘tkazib yuborildi.")
                    continue

                success_count = 0
                error_count = 0

                for target in targets[:15]:  # bir martada 15 tadan yuborish
                    print(f"➡ Jo‘natilmoqda: {target.chat_id}")
                    try:
                        async with session.post(
                            f"{TELEGRAM_API_URL}/forwardMessage",
                            data={
                                "chat_id": target.chat_id,
                                "from_chat_id": ad.forward_from_chat_id,
                                "message_id": ad.forward_message_id
                            }
                        ) as resp:
                            result = await resp.json()
                            if result.get("ok"):
                                print(f"✅ Muvaffaqiyatli: {target.chat_id}")
                                await sync_to_async(AdvertisementHistory.objects.create)(
                                    advertisement=ad,
                                    chat_id=target.chat_id,
                                    title=getattr(target, "title", getattr(target, "full_name", "")),
                                    is_success=True
                                )
                                success_count += 1
                            else:
                                err_desc = result.get("description", "Noma’lum xato")
                                print(f"⚠️ Xato: {target.chat_id} | Sabab: {err_desc}")
                                await sync_to_async(AdvertisementHistory.objects.create)(
                                    advertisement=ad,
                                    chat_id=target.chat_id,
                                    title=getattr(target, "title", getattr(target, "full_name", "")),
                                    is_success=False,
                                    description=err_desc
                                )
                                error_count += 1

                    except Exception as e:
                        print(f"❌ Exception: {target.chat_id} | {str(e)}")
                        await sync_to_async(AdvertisementHistory.objects.create)(
                            advertisement=ad,
                            chat_id=target.chat_id,
                            title=getattr(target, "title", getattr(target, "full_name", "")),
                            is_success=False,
                            description=str(e)
                        )
                        error_count += 1

                    await asyncio.sleep(0.2)  # flood control xavfini kamaytirish

                # Statistikani yangilash
                ad.success += success_count
                ad.error += error_count
                await sync_to_async(ad.save)()
                print(f"📊 Statistikaga qo‘shildi | Success: {success_count}, Error: {error_count}")

                # Tugaganini tekshirish
                total_targets = await sync_to_async(lambda: (
                    TgUser.objects.count() if ad.target_type == Advertisement.TARGET_USERS
                    else TgGroup.objects.count()
                ))()
                sent_count = await sync_to_async(lambda: AdvertisementHistory.objects.filter(advertisement=ad).count())()

                if sent_count >= total_targets:
                    ad.is_sent = True
                    await sync_to_async(ad.save)()
                    print("🏁 Reklama tugadi, admin’ga xabar yuborilmoqda...")
                    await session.post(
                        f"{TELEGRAM_API_URL}/sendMessage",
                        data={
                            "chat_id": ad.created_by,
                            "text": f"✅ Reklama tugadi\nMuvaffaqiyatli: {ad.success}\nXato: {ad.error}"
                        }
                    )

        print("🎉 Jarayon yakunlandi.")
        return HttpResponse("OK")

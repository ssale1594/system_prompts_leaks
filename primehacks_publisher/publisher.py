"""
PrimeHacksDaily — أداة النشر التلقائي
تدخل رابط أمازون → تنشر تلقائياً على Facebook و Instagram
"""

import requests
import json
import sys
from pathlib import Path

# ──────────────────────────────────────────────
# الإعدادات — عدّل هنا فقط
# ──────────────────────────────────────────────
META_TOKEN = "EAAWalYZAGzsMBRkqYSXRZCGZCKEgQ5vdfbWDYVrggRlPmZCVax5bHRbLauZBOyKmV8YynoDxzTOaigY7WWBUyZAtDmHHlpVXIt8ZCN0Ny6usN8oDihHHQjFdiLku3WZCYpSIEbFoHl67ZA3y4dFZBcZBDsWc1sr3aeYXGlohrHgPDbzjov6ZCJikzq1AXQmGPO7I11ZBjPqEJ5ZCQho247FIqWZBMhZA5ZBZBhLu4bmlMewAVVdISXVGeIJLtwoNGL1qQp7d1FAgIedSpeAGZC1Jv5Gb9MhMqtaAt5hmishNY6c2QZDZD"
PAGE_NAME = "Primehacksdaily"
AMAZON_TAG = "newwave5077-20"

# ──────────────────────────────────────────────
# الحصول على Page ID و Instagram ID
# ──────────────────────────────────────────────

def get_page_info():
    url = f"https://graph.facebook.com/v19.0/me/accounts"
    r = requests.get(url, params={"access_token": META_TOKEN})
    data = r.json()

    if "error" in data:
        print(f"❌ خطأ Meta: {data['error']['message']}")
        return None, None, None

    for page in data.get("data", []):
        if PAGE_NAME.lower() in page["name"].lower():
            page_id = page["id"]
            page_token = page["access_token"]

            # جيب Instagram ID
            ig_r = requests.get(
                f"https://graph.facebook.com/v19.0/{page_id}",
                params={"fields": "instagram_business_account", "access_token": page_token}
            ).json()
            ig_id = ig_r.get("instagram_business_account", {}).get("id")

            print(f"✅ صفحة: {page['name']} (ID: {page_id})")
            print(f"✅ Instagram ID: {ig_id}" if ig_id else "⚠️  ما لقينا Instagram مرتبط")
            return page_id, page_token, ig_id

    print(f"❌ ما لقينا صفحة باسم '{PAGE_NAME}'")
    print("الصفحات المتاحة:", [p["name"] for p in data.get("data", [])])
    return None, None, None


# ──────────────────────────────────────────────
# النشر على Facebook
# ──────────────────────────────────────────────

def post_facebook(page_id, page_token, message, image_url=None):
    if image_url:
        url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
        params = {
            "url": image_url,
            "caption": message,
            "access_token": page_token,
        }
    else:
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        params = {
            "message": message,
            "access_token": page_token,
        }

    r = requests.post(url, data=params)
    data = r.json()

    if "error" in data:
        print(f"❌ Facebook: {data['error']['message']}")
        return False
    print(f"✅ نُشر على Facebook! ID: {data.get('id', data.get('post_id'))}")
    return True


# ──────────────────────────────────────────────
# النشر على Instagram
# ──────────────────────────────────────────────

def post_instagram(ig_id, page_token, message, image_url):
    if not ig_id:
        print("⚠️  تخطي Instagram — ما في حساب مرتبط")
        return False

    if not image_url:
        print("⚠️  Instagram يحتاج صورة للنشر")
        return False

    # خطوة 1: رفع الصورة
    container_r = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_id}/media",
        data={
            "image_url": image_url,
            "caption": message,
            "access_token": page_token,
        }
    ).json()

    if "error" in container_r:
        print(f"❌ Instagram upload: {container_r['error']['message']}")
        return False

    container_id = container_r.get("id")

    # خطوة 2: نشر
    publish_r = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": page_token,
        }
    ).json()

    if "error" in publish_r:
        print(f"❌ Instagram publish: {publish_r['error']['message']}")
        return False

    print(f"✅ نُشر على Instagram! ID: {publish_r.get('id')}")
    return True


# ──────────────────────────────────────────────
# توليد المحتوى
# ──────────────────────────────────────────────

def generate_post(product_name, price, amazon_url, custom_text=""):
    if custom_text:
        return custom_text

    return f"""🔥 {product_name}

💰 السعر: ${price}
✅ متوفر على أمازون

🛒 اشترِ الآن:
{amazon_url}

#AmazonFinds #PrimeHacksDaily #KitchenHacks #SmartGadgets"""


# ──────────────────────────────────────────────
# الواجهة الرئيسية
# ──────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  PrimeHacksDaily — ناشر المحتوى التلقائي")
    print("=" * 50)
    print()

    # جيب معلومات الصفحة
    print("🔍 جاري التحقق من حسابات Meta...")
    page_id, page_token, ig_id = get_page_info()
    if not page_id:
        return

    print()
    print("📝 أدخل معلومات المنتج:")
    product_name = input("اسم المنتج: ").strip()
    price = input("السعر ($): ").strip()
    amazon_url = input("رابط أمازون: ").strip()
    image_url = input("رابط صورة المنتج (اختياري): ").strip() or None
    custom_text = input("نص مخصص (اتركه فارغاً للتلقائي): ").strip()

    print()
    message = generate_post(product_name, price, amazon_url, custom_text)

    print("📋 المحتوى الذي سيُنشر:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    print()

    confirm = input("تأكيد النشر؟ (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ تم الإلغاء")
        return

    print()
    print("🚀 جاري النشر...")
    post_facebook(page_id, page_token, message, image_url)
    if ig_id and image_url:
        post_instagram(ig_id, page_token, message, image_url)

    print()
    print("✅ اكتمل!")


if __name__ == "__main__":
    main()

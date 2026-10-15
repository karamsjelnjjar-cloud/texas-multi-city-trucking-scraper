import asyncio
import re
import string
import pandas as pd

from playwright.async_api import async_playwright


all_companies = []

# عدد الصفحات المتزامنة لتفادي حظر الموقع
MAX_CONCURRENT_PAGES = 2
semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)


# ==========================================
# 1. استخراج أول 3 مدن من كل حرف بالترتيب الأبجدي (A-Z)
# ==========================================
async def get_top_cities_per_letter(context):
    texas_url = "https://www.quicktransportsolutions.com/carrier/texas/trucking-companies.php"
    page = await context.new_page()
    selected_cities = []

    try:
        print("🔍 Extracting top 3 cities for each letter in alphabetical order (A-Z)...")

        await page.goto(
            texas_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # الانتظار حتى تحميل الجداول
        await page.wait_for_selector("table", timeout=15000)

        # جلب كل روابط المدن من خلايا الجدول (td width=10%) بنفس ترتيبها في الصفحة
        all_links = await page.evaluate("""
            () => {
                const result = [];
                document.querySelectorAll("td[width='10%'] a[href$='.php']").forEach(a => {
                    result.push({
                        name: (a.textContent || "").trim(),
                        href: a.getAttribute("href") || ""
                    });
                });
                return result;
            }
        """)

        print(f"  🔗 Found {len(all_links)} city links on the page.")

        # تجميع المدن حسب أول حرف من اسم المدينة
        cities_by_letter = {letter: [] for letter in string.ascii_uppercase}

        for item in all_links:
            href = item["href"]
            name = item["name"]

            if not href or not name:
                continue

            # استبعاد الروابط غير المرغوبة
            if "trucking-companies.php" in href or len(name) < 2:
                continue

            # روابط المدن نسبية فقط مثل dale.php (بدون مسار أو http)
            if href.startswith("http") or "/" in href:
                continue

            # الحرف الأول من اسم المدينة
            letter = name[0].upper()

            if letter not in cities_by_letter:
                continue

            # بناء الرابط الكامل
            full_url = "https://www.quicktransportsolutions.com/carrier/texas/" + href

            letter_cities = cities_by_letter[letter]

            # الاكتفاء بأول 3 مدن فقط لكل حرف، بدون تكرار
            if len(letter_cities) < 3 and not any(c["url"] == full_url for c in letter_cities):
                letter_cities.append({"name": name, "url": full_url, "letter": letter})

        # المرور على الحروف بالترتيب من A إلى Z
        for letter in string.ascii_uppercase:
            letter_cities = cities_by_letter[letter]

            if letter_cities:
                print(f"  🔤 Letter [{letter}]: Selected {len(letter_cities)} cities -> "
                      f"{', '.join(c['name'] for c in letter_cities)}")
                selected_cities.extend(letter_cities)

        print(f"\n✅ Successfully selected total {len(selected_cities)} cities across all letters (A-Z)!")
        return selected_cities

    except Exception as e:
        print(f"❌ Error collecting city links: {e}")
        return []

    finally:
        await page.close()


# ==========================================
# 2. استخراج الشركات من كل مدينة
# ==========================================
async def scrape_city_companies(context, city_name, city_url, max_pages=1):
    for page_num in range(1, max_pages + 1):
        page_url = f"{city_url}?page={page_num}" if "?page=" not in city_url else city_url
        page = await context.new_page()

        try:
            print(f"\n🌆 [{city_name}] Scraping Page {page_num}...")

            await page.goto(
                page_url,
                wait_until="domcontentloaded",
                timeout=50000
            )

            links = page.locator('a[href*="/truckingcompany/texas/"]')
            count = await links.count()

            if count == 0:
                await page.close()
                break

            company_links = []
            for i in range(count):
                href = await links.nth(i).get_attribute("href")
                if href and "carrierregister.php" not in href:
                    if href.startswith("/"):
                        href = "https://www.quicktransportsolutions.com" + href
                    company_links.append(href)

            company_links = list(dict.fromkeys(company_links))

            tasks = [
                scrape_company_details(context, url, city_name)
                for url in company_links
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            print(f"❌ Error in city {city_name} page {page_num}: {e}")

        finally:
            await page.close()


# ==========================================
# 3. استخراج بيانات تفاصيل الشركة
# ==========================================
async def scrape_company_details(context, url, city_name):
    async with semaphore:
        page = None

        try:
            page = await context.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=45000
            )

            company_name = "N/A"
            phone = "N/A"
            usdot = "N/A"
            trucks = "N/A"
            drivers = "N/A"

            h1 = page.locator("h1")

            if await h1.count() > 0:
                company_name = await h1.text_content()

                if company_name:
                    company_name = company_name.strip()

            page_text = await page.locator("body").inner_text()

            # Phone
            phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", page_text)
            if phone_match:
                phone = phone_match.group().strip()

            # USDOT
            usdot_match = re.search(r"USDOT[#\s:]*(\d+)", page_text, re.IGNORECASE)
            if usdot_match:
                usdot = usdot_match.group(1).strip()

            # Trucks
            trucks_match = re.search(r"Trucks:\s*(\d+)", page_text, re.IGNORECASE)
            if trucks_match:
                trucks = trucks_match.group(1).strip()

            # Drivers
            drivers_match = re.search(r"Drivers:\s*(\d+)", page_text, re.IGNORECASE)
            if drivers_match:
                drivers = drivers_match.group(1).strip()

            all_companies.append({
                "Company Name": company_name,
                "Phone": phone,
                "Trucks": trucks,
                "Drivers": drivers,
                "City": city_name,
                "State": "Texas",
                "USDOT": usdot,
                "Source URL": url
            })

            print(f"  ✅ [{city_name}] {company_name} | Phone: {phone}")

        except Exception as e:
            print(f"  ❌ Company Error ({url}): {e}")

        finally:
            if page:
                await page.close()
            # استراحة قصيرة جداً لتجنب حظر الخادم
            await asyncio.sleep(1)


# ==========================================
# 4. تصدير البيانات إلى Excel
# ==========================================
def export_to_excel():
    if not all_companies:
        print("❌ No data extracted!")
        return

    clean_data = [c for c in all_companies if c["Company Name"] != "N/A"]

    df = pd.DataFrame(clean_data)
    file_name = "texas_top3_cities_per_letter.xlsx"
    df.to_excel(file_name, index=False)

    print(f"\n🎉 File saved successfully: {file_name}")
    print(f"📊 Total Companies Extracted Across Texas Cities: {len(clean_data)}")


# ==========================================
# 5. Main Execution
# ==========================================
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        cities = await get_top_cities_per_letter(context)

        if cities:
            print(f"\n🚚 Processing {len(cities)} cities in Texas sequentially...")

            for city in cities:
                await scrape_city_companies(context, city["name"], city["url"], max_pages=1)

        await browser.close()

    export_to_excel()


if __name__ == "__main__":
    asyncio.run(main())
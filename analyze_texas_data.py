import pandas as pd

# قراءة الملف الذي تم استخراجه مسبقاً
file_name = "texas_top3_cities_per_letter.xlsx"
df = pd.read_excel(file_name)

print(f"📊 Original Data Count: {len(df)} companies")

# تنظيف وتحويل الأعمدة الرقمية (Trucks & Drivers) إلى أرقام صحيحة
df["Trucks"] = pd.to_numeric(df["Trucks"], errors="coerce").fillna(0)
df["Drivers"] = pd.to_numeric(df["Drivers"], errors="coerce").fillna(0)

# 1. ترتيب الشركات تنازلياً حسب أكثر شركة امتلاكاً للشاحنات
top_trucks_companies = df.sort_values(by="Trucks", ascending=False).head(10)
print("\n🚚 Top 10 Companies by Number of Trucks:")
print(
    top_trucks_companies[
        ["Company Name", "City", "Trucks", "Drivers", "Phone", "USDOT"]
    ]
)

# 2. تجميع البيانات حسب المدينة لمعرفة أي المدن تضم أكبر عدد إجمالي من الشاحنات والسائقين
city_summary = (
    df.groupby("City")[["Trucks", "Drivers"]]
    .sum()
    .reset_index()
    .sort_values(by="Trucks", ascending=False)
)

print("\n🏙️ Top Cities by Total Trucks & Drivers:")
print(city_summary.head(10))

# 3. حفظ نتائج التحليل في ملف إكسل جديد منظم
output_analysis_file = "texas_trucks_analysis.xlsx"
with pd.ExcelWriter(output_analysis_file, engine="openpyxl") as writer:
    df.sort_values(by="Trucks", ascending=False).to_excel(
        writer, sheet_name="All Companies Sorted", index=False
    )
    city_summary.to_excel(writer, sheet_name="City Summary", index=False)

print(f"\n🎉 Analysis report saved successfully to: {output_analysis_file}")
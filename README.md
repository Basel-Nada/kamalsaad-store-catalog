# كتالوج متجر كمال سعد | KMS Store Catalog

موقع كتالوج تفاعلي وسريع لمتجر كمال سعد يضم أكثر من 1,900+ منتج مع إمكانية البحث والفلترة والطلب، ومزود بنظام **مزامنة وتحديث تلقائي دوري سحابياً** دون أي تدخل يدوي عبر GitHub Actions و Vercel.

---

## 🚀 طريقة الرفع والتشغيل على Vercel مع التحديث التلقائي

### الخطوة 1: إنشاء مستودع جديد على GitHub
1. ادخل على حسابك في [GitHub.com](https://github.com/) واضغط **New Repository**.
2. سمِّ المستودع مثلاً: `kamal-saad-catalog`.
3. اجعل المستودع **Public** أو **Private** واضغط **Create repository**.

### الخطوة 2: رفع ملفات المجلد إلى GitHub
من داخل موجه الأوامر (Terminal) داخل مجلد `web`:
```bash
git init
git add .
git commit -m "Initial commit: KMS Store Catalog with Auto-Sync"
git branch -M main
git remote add origin https://github.com/USERNAME/kamal-saad-catalog.git
git push -u origin main
```
*(استبدل `USERNAME` باسم حسابك على GitHub)*

### الخطوة 3: تفعيل صلاحيات الكتابة لـ GitHub Actions (ضرورية للتحديث التلقائي)
1. في صفحة المستودع على GitHub، اذهب إلى: **Settings** -> **Actions** -> **General**.
2. انزل إلى قسم **Workflow permissions**.
3. اختر: **Read and write permissions**.
4. اضغط **Save**.

### الخطوة 4: ربط المستودع بـ Vercel
1. ادخل على حسابك في [Vercel.com](https://vercel.com/) واضغط **Add New... -> Project**.
2. اختر مستودع `kamal-saad-catalog` واضغط **Import**.
3. اضغط **Deploy** مباشرة بدون أي تعديلات.

🎉 **مبروك!** موقعك الآن يعمل على رابط مجاني مثل `https://kamal-saad-catalog.vercel.app` ومربوط بالتحديث التلقائي يومياً!

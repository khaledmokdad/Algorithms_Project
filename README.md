# Algorithms_Project

## توزيع المهام على آلات غير متطابقة

**BIA601 — Intelligent Algorithms / الخوارزميات الذكية (F25) — المجموعة 3**

المستودع: https://github.com/khaledmokdad/Algorithms_Project

مشروع جدولة مهام على آلات متوازية غير متطابقة، بهدف تقليل زمن انتهاء آخر آلة (Makespan). نقارن خوارزمية جينية (GA) وأسراب الجسيمات (PSO) ومستعمرة النمل (ACO) مع حل جشع مشترك وحد أدنى خطي.

Heterogeneous parallel-machine task scheduling: assign each job to one machine to minimize makespan, using GA, PSO, and ACO.

## فريق العمل — Group 3

| العضو | GitHub | المسؤولية | القضية |
|---|---|---|---|
| خالد المقداد | [khaledmokdad](https://github.com/khaledmokdad) | التكامل النهائي والتوثيق | [#9](https://github.com/khaledmokdad/Algorithms_Project/issues/9) |
| ريتا حمادة | [rita-emp23](https://github.com/rita-emp23) | نموذج المسألة والحل الجشع والحد الأدنى | [#1](https://github.com/khaledmokdad/Algorithms_Project/issues/1) |
| مجد عرابي | [Majd20011](https://github.com/Majd20011) | خوارزمية GA | [#2](https://github.com/khaledmokdad/Algorithms_Project/issues/2) |
| نيرمين محمود | [Nirmen-191627](https://github.com/Nirmen-191627) | خوارزمية PSO | [#3](https://github.com/khaledmokdad/Algorithms_Project/issues/3) |
| ميار الخلف | [mayaralkhalaf](https://github.com/mayaralkhalaf) | خوارزمية ACO | [#4](https://github.com/khaledmokdad/Algorithms_Project/issues/4) |
| عبد الستار الصياد | [Abdulsattar120](https://github.com/Abdulsattar120) | منصة التجارب والتصدير والنتائج | [#5](https://github.com/khaledmokdad/Algorithms_Project/issues/5) |
| محمد الزيات | [tysonmj00-byte](https://github.com/tysonmj00-byte) | التحقق من البيانات والإسنادات | [#6](https://github.com/khaledmokdad/Algorithms_Project/issues/6) |
| عبدالله رمضان | [Abdllauhramdan](https://github.com/Abdllauhramdan) | واجهة العرض التفاعلية | [#7](https://github.com/khaledmokdad/Algorithms_Project/issues/7) |
| محمد طارق بابا | [tarekbaba183-dot](https://github.com/tarekbaba183-dot) | التقرير النهائي | [#8](https://github.com/khaledmokdad/Algorithms_Project/issues/8) |

مساهمة كل عضو موثّقة في التقرير (`Report.docx`، جدول 7) وفي تاريخ المستودع.

## التشغيل

Python 3.12 أو أحدث، من مجلد `project`:

```text
python -m pip install -r requirements.txt
python main.py
python verify.py
```

تجربة قصيرة تكتب في مجلد مستقل:

```text
python main.py --runs 2 --output ../trial_results
```

إعادة أول تشغيلة لكل خوارزمية ولكل مسألة، مع فحص سجل التقارب كاملا:

```text
python verify.py --rerun
```

التفاصيل التقنية والإعدادات موجودة في [`project/README.md`](project/README.md). الإعدادات المستخدمة في [`project/settings.json`](project/settings.json).

## النتائج والعرض

- التقرير: [`Report.docx`](Report.docx) ونسخة PDF للتسليم: [`Report.pdf`](Report.pdf)
- لوحة النتائج التفاعلية: افتح [`index.html`](index.html) في المتصفح (ملف مستقل، لا يحتاج تشغيل خادم).
لعرض الجداول والرسوم بعد التجربة الكاملة يكفي فتح الملف محلياً.
- مخرجات التجارب والرسوم: [`project/results/`](project/results/)

## مخرجات التسليم

المشروع جاهز للتسليم قبل 12 نوفمبر 2026، ويتضمن:

1. الكود المصدري القابل للتشغيل في `project/` (GA و PSO و ACO من الصفر، مع حل جشع وحد أدنى خطي).
2. تقريراً مختصراً يشرح المسألة والخوارزميات والتجارب والنتائج ومهمة كل عضو (`Report.docx` و`Report.pdf`).
3. ملف `README.md` هذا مع تعليمات التشغيل وإعادة التجربة عبر `verify.py`.

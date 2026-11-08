# Algorithms_Project

## توزيع المهام على آلات غير متطابقة

**BIA601 — Intelligent Algorithms / الخوارزميات الذكية — الوظيفة الثانية (F25)**

مشروع جدولة مهام على آلات متوازية غير متطابقة، بهدف تقليل زمن انتهاء آخر آلة (Makespan). نقارن خوارزمية جينية (GA) وأسراب الجسيمات (PSO) ومستعمرة النمل (ACO) مع حل جشع مشترك وحد أدنى خطي.

Heterogeneous parallel-machine task scheduling: assign each job to one machine to minimize makespan, using GA, PSO, and ACO.

## فريق العمل — Group 3

| العضو | GitHub | المسؤولية |
|---|---|---|
| خالد مقداد | [khaledmokdad](https://github.com/khaledmokdad) | التكامل النهائي والتوثيق |
| ريتا | [rita-emp23](https://github.com/rita-emp23) | نموذج المسألة والحل الجشع والحد الأدنى |
| مجد | [Majd20011](https://github.com/Majd20011) | خوارزمية GA |
| نيرمين | [Nirmen-191627](https://github.com/Nirmen-191627) | خوارزمية PSO |
| ميار | [mayaralkhalaf](https://github.com/mayaralkhalaf) | خوارزمية ACO |
| عبد الستار | [Abdulsattar120](https://github.com/Abdulsattar120) | منصة التجارب والتصدير والنتائج |
| تايسون | [tysonmj00-byte](https://github.com/tysonmj00-byte) | التحقق من البيانات والإسنادات |
| عبد الله رمضان | [Abdllauhramdan](https://github.com/Abdllauhramdan) | واجهة العرض التفاعلية |
| طارق | [tarekbaba183-dot](https://github.com/tarekbaba183-dot) | التقرير النهائي |

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

- التقرير: [`Report.docx`](Report.docx)
- لوحة النتائج التفاعلية: افتح [`index.html`](index.html) في المتصفح
- مخرجات التجارب والرسوم: [`project/results/`](project/results/)

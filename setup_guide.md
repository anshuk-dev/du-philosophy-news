# 🚀 DU Philosophy Vacancy Alert - 100% Free Setup Guide (हिंदी गाइड)

यह सिस्टम दिल्ली यूनिवर्सिटी (DU) के सभी कॉलेजों और दर्शनशास्त्र (Philosophy) विभाग में निकलने वाले **Guest Faculty**, **Ad-hoc Panel**, और **Permanent Assistant Professor** के विज्ञापनों और वॉक-इन इंटरव्यू को अपने आप ट्रैक करता है और नया नोटिस आते ही **`anshu.philosophy@gmail.com`** पर ईमेल भेज देता है।

> ⚡ **यह सेटअप 100% फ्री है!** इसके लिए किसी पेड सर्वर या डोमेन की ज़रूरत नहीं है। यह GitHub Actions के फ्री टियर पर 24×7 हमेशा चलता रहेगा।

---

## 📌 यह सिस्टम क्या-क्या ट्रैक करता है?
1. **DU Central Portal (`work-with-du`)**: सभी कॉलेजों के Guest Faculty और Walk-in इंटरव्यू विज्ञापन (Ramjas, Hindu, Hansraj, Gargi, LSR, Kamala Nehru, KMC आदि)।
2. **DU Philosophy Department (`philosophy.du.ac.in`)**: Ad-hoc पैनल लिस्ट, इंटरव्यू शेड्यूल और डिपार्टमेंटल नोटिस।
3. **DU Colrec & Samarth Portal (`colrec.uod.ac.in`)**: कॉलेजों में असिस्टेंट प्रोफेसर की परमानेंट वेकेंसी।
4. **Real-time News & RSS Feeds**: किसी भी कॉलेज की अचानक आने वाली वॉक-इन इंटरव्यू सूचना।
5. **Smart Date Filtering**: केवल **Current** और **Upcoming** (वर्तमान और आने वाली) वेकेंसी फ़िल्टर होती हैं, पुराने (past/expired) नोटिस नहीं भेजे जाते।

---

## 🛠️ सिर्फ 3 स्टेप्स में चालू करें (2 मिनट का काम)

### स्टेप 1: GitHub पर फ्री रिपॉजिटरी बनाएं और कोड अपलोड करें
1. [github.com](https://github.com) पर जाएं और लॉगिन करें।
2. ऊपर दाएँ कोने में `+` पर क्लिक करके **New repository** चुनें।
3. रिपॉजिटरी का नाम रखें: `du-philosophy-news` (Public या Private कोई भी चुन सकते हैं)।
4. अपने कंप्यूटर के टर्मिनल में इस फोल्डर (`DU news daily`) में जाकर ये कमांड्स चलाएं:

```bash
cd "/Users/anshu_macmini/Downloads/DU news daily"
git init
git add .
git commit -m "Initial commit: DU Philosophy Faculty Alert System"
git branch -M main
git remote add origin https://github.com/APNA_GITHUB_USERNAME/du-philosophy-news.git
git push -u origin main
```
*(नोट: `APNA_GITHUB_USERNAME` की जगह अपना गिटहब यूजरनेम लिखें)*

---

### स्टेप 2: गूगल से फ्री "App Password" प्राप्त करें (1 मिनट)
Gmail से ऑटोमेटिक ईमेल भेजने के लिए Google का फ्री 16-अक्षरों वाला App Password चाहिए होता है:

1. अपने Google Account पर जाएं: [myaccount.google.com/security](https://myaccount.google.com/security)
2. सुनिश्चित करें कि **2-Step Verification** ऑन (On) हो।
3. सर्च बार में लिखें **"App passwords"** (या [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) पर जाएं)।
4. App name में लिखें: `DU Alert Bot` और **Create** पर क्लिक करें।
5. स्क्रीन पर 16 अक्षरों का एक पासवर्ड दिखेगा (जैसे `abcd efgh ijkl mnop`)। इसे कॉपी कर लें।

---

### स्टेप 3: GitHub Secrets में पासवर्ड सेव करें
1. अपनी GitHub रिपॉजिटरी के पेज पर जाएं।
2. ऊपर **Settings** टैब पर क्लिक करें।
3. बाएँ मेन्यू में **Secrets and variables** -> **Actions** पर क्लिक करें।
4. **New repository secret** बटन दबाएं और 2 सीक्रेट्स जोड़ें:

| Secret Name | Secret Value (क्या डालना है) |
|---|---|
| `GMAIL_USER` | आपका ईमेल: `anshu.philosophy@gmail.com` |
| `GMAIL_APP_PASSWORD` | स्टेप 2 में मिला 16 अक्षरों का पासवर्ड |

---

## 🎯 टेस्ट कैसे करें?
1. अपने गिटहब रिपॉजिटरी में **Actions** टैब पर जाएं।
2. बायीं तरफ **DU Philosophy Faculty Vacancy Alert** पर क्लिक करें।
3. दाएँ कोने में **Run workflow** -> हरा बटन **Run workflow** दबाएं।
4. 15-20 सेकंड में बॉट चलेगा, सारी साइट्स स्कैन करेगा, और सीधे आपकी ईमेल `anshu.philosophy@gmail.com` पर नोटिस भेज देगा!

---

## ⏰ ऑटोमेटिक टाइमिंग
अब आपको कुछ नहीं करना है! GitHub Actions हर रोज़ 3 बार अपने आप चलेगा:
- 🌅 सुबह: **9:00 AM IST**
- ☀️ दोपहर: **3:00 PM IST**
- 🌙 रात: **9:00 PM IST**

जैसे ही कोई नया नोटिस DU या किसी कॉलेज की वेबसाइट पर आएगा, आपको तुरंत ईमेल मिल जाएगा!

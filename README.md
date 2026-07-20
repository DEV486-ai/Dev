# পাতা চা বাগান — অনলাইন শপ

সিলেট অঞ্চলের চা বিক্রির জন্য একটা ছোট ই-কমার্স ওয়েবসাইট।

## ফাইল গঠন

- index.html — হোমপেজ
- style.css — ডিজাইন
- products.js — পণ্যের তালিকা (এখানে এডিট করলেই সাইটে আপডেট হবে)
- script.js — পণ্য দেখানো ও অর্ডার ফর্ম
- app.py — Flask ব্যাকএন্ড (অর্ডার সেভ করার জন্য)
- requirements.txt — Python প্যাকেজ তালিকা
- firebase.json — Firebase Hosting কনফিগ

## চালানো

শুধু স্ট্যাটিক সাইট দেখতে (GitHub Pages/Firebase Hosting):
সরাসরি লিংকে যান — অর্ডার ফর্ম ছাড়া সব কাজ করবে।

পূর্ণাঙ্গ (অর্ডার ফর্মসহ) চালাতে:
pip install -r requirements.txt
python3 app.py

তারপর ব্রাউজারে: http://127.0.0.1:5000

## লাইসেন্স

GPL-3.0

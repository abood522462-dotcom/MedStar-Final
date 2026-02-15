// static/main.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // 1. دالة البحث الفوري عن الدكاترة
    // ============================================
    const searchInput = document.getElementById('doctorSearchInput');
    
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            const term = e.target.value.toLowerCase();
            const doctors = document.querySelectorAll('.services__card'); // كروت الدكاترة

            doctors.forEach(function(doctor) {
                // بنبحث في الاسم والتخصص
                const name = doctor.querySelector('h3').textContent.toLowerCase();
                const specialty = doctor.querySelector('p').textContent.toLowerCase();

                if (name.includes(term) || specialty.includes(term)) {
                    doctor.style.display = 'block'; // اظهر الكارت
                    doctor.style.animation = 'fadeIn 0.5s'; // حركة ناعمة
                } else {
                    doctor.style.display = 'none'; // اخفي الكارت
                }
            });
        });
    }

    // ============================================
    // 2. دالة إخفاء الرسائل أوتوماتيكياً
    // ============================================
    // (عشان تشتغل لازم تدي الرسايل في الـ HTML كلاس اسمه flash-message)
    const alerts = document.querySelectorAll('.flash-message'); 
    
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                alert.style.transition = "opacity 1s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 1000); // يشيلها من الصفحة خالص بعد ما تختفي
            });
        }, 3000); // استنى 3 ثواني وبعدين ابدأ الاختفاء
    }

});

// إضافة حركة CSS بسيطة في ملف الـ JS نفسه (اختياري بس شيك)
const style = document.createElement('style');
style.innerHTML = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);
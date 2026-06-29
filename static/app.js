// دالة تنفيذ الأوامر مباشرة
async function executeCommand(command) {
    if (!command) return;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم تنفيذ الأمر: ${command}`);
            addToCommandLog(command, 'success');
        } else {
            showToast('فشل في تنفيذ الأمر: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(command, 'error');
        }
    } catch (error) {
        console.error('خطأ في تنفيذ الأمر:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(command, 'error');
    }
}

// دالة نسخ الأوامر (للاستخدام الاختياري)
function copyCommand(command) {
    if (!command) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(command).then(function() {
            showToast(`تم نسخ الأمر: ${command}`);
        }).catch(function(err) {
            console.error('فشل في نسخ الأمر:', err);
            fallbackCopy(command);
        });
    } else {
        fallbackCopy(command);
    }
}

// نسخ احتياطي للأوامر
function fallbackCopy(command) {
    try {
        const textArea = document.createElement('textarea');
        textArea.value = command;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast(`تم نسخ الأمر: ${command}`);
    } catch (err) {
        console.error('فشل في النسخ الاحتياطي:', err);
        showToast(`فشل في نسخ الأمر: ${command}`);
    }
}

// دالة توليد رقم عشوائي للرقصات وتنفيذه
async function generateRandomNumber() {
    const randomNum = Math.floor(Math.random() * 183) + 1;
    await executeCommand(`عشوائي`);
}

// متغيرات للتحكم في الرقصات
let botAutoEmoteActive = false;
let userRepeatedEmoteActive = false;
let allEmotesData = [];
let currentUsers = [];

// تحميل البيانات من API
async function loadBotData() {
    try {
        // تحميل بيانات المستخدمين
        try {
            const usersResponse = await fetch('/api/users');
            if (usersResponse.ok) {
                const usersData = await usersResponse.json();

                // تحديث إحصائيات المستخدمين
                const activeUsersElement = document.querySelector('.stats-active-users');
                const totalUsersElement = document.querySelector('.stats-total-users');

                if (activeUsersElement) {
                    activeUsersElement.textContent = usersData.active_users || 0;
                }
                if (totalUsersElement) {
                    totalUsersElement.textContent = usersData.total_users || 0;
                }
            }
        } catch (error) {
            console.error('خطأ في تحميل بيانات المستخدمين:', error);
        }

        // تحميل بيانات الرقصات
        try {
            const emotesResponse = await fetch('/api/emotes');
            if (emotesResponse.ok) {
                const emotesData = await emotesResponse.json();

                if (emotesData.emotes_list && Array.isArray(emotesData.emotes_list)) {
                    loadEmotesList(emotesData.emotes_list);
                } else {
                    console.warn('بيانات الرقصات غير صحيحة');
                    // إظهار رسالة في قائمة الرقصات
                    const emotesList = document.getElementById('emotesList');
                    if (emotesList) {
                        emotesList.innerHTML = '<div class="text-center text-muted">لم يتم تحميل قائمة الرقصات</div>';
                    }
                }
            }
        } catch (error) {
            console.error('خطأ في تحميل بيانات الرقصات:', error);
        }

        // تحميل المستخدمين الحقيقيين
        await loadUsersForSelection();

    } catch (error) {
        console.error('خطأ عام في تحميل البيانات:', error);
    }
}

// تحميل قائمة الرقصات
function loadEmotesList(emotes) {
    allEmotesData = emotes;
    const emotesList = document.getElementById('emotesList');

    if (emotesList) {
        let html = '';
        emotes.forEach((emote, index) => {
            const number = index + 1;
            html += `
                <div class="emote-item d-flex justify-content-between align-items-center py-1 px-2 border-bottom" 
                     style="cursor: pointer; font-size: 12px;" 
                     onclick="copyEmoteNumber(${number})" 
                     title="انقر لنسخ رقم الرقصة">
                    <span><strong>${number}.</strong> ${emote}</span>
                    <small class="text-muted">#${number}</small>
                </div>
            `;
        });
        emotesList.innerHTML = html;
    }
}

// تنفيذ رقصة بالرقم المحدد
async function copyEmoteNumber(number) {
    await executeCommand(`رقص ${number}`);
}

// تحميل المستخدمين الحقيقيين من الغرفة مباشرة
async function loadUsersForSelection() {
    try {
        console.log('🔄 جاري تحديث قائمة المستخدمين من الغرفة...');

        const response = await fetch('/api/room-users');
        if (response.ok) {
            const data = await response.json();

            // فحص إذا كانت البيانات صحيحة
            if (!data || !data.users || !Array.isArray(data.users)) {
                console.error('بيانات المستخدمين غير صحيحة:', data);
                showToast('❌ خطأ في بيانات المستخدمين');
                return;
            }

            const users = data.users;
            currentUsers = users;

            // جميع المستخدمين في القائمة نشطين (في الغرفة)
            const activeUsers = users;

            // تحديث قائمة اختيار المستخدمين في مدير الرقصات
            const userSelect = document.getElementById('userSelect');
            if (userSelect) {
                userSelect.innerHTML = '<option value="">📋 اختر مستخدم من الغرفة...</option>';
                activeUsers.forEach(user => {
                    const userInfo = getUserDisplayInfo(user);
                    userSelect.innerHTML += `<option value="@${user.username}">${userInfo.emoji} ${user.username} - ${userInfo.type}</option>`;
                });

                // إضافة عداد المستخدمين
                if (activeUsers.length > 0) {
                    const countOption = document.createElement('option');
                    countOption.disabled = true;
                    countOption.innerHTML = `═══ ${activeUsers.length} مستخدم في الغرفة ═══`;
                    userSelect.insertBefore(countOption, userSelect.children[1]);
                }
            }

            // تحديث قائمة التحكم في المستخدمين
            const controlSelect = document.getElementById('controlUsername');
            if (controlSelect) {
                controlSelect.innerHTML = '<option value="">🎮 اختر مستخدم للتحكم...</option>';
                activeUsers.forEach(user => {
                    const userInfo = getUserDisplayInfo(user);
                    controlSelect.innerHTML += `<option value="@${user.username}">${userInfo.emoji} ${user.username} - ${userInfo.type}</option>`;
                });
            }



            // تحديث قائمة الهدف للرقص
            const targetSelect = document.getElementById('targetUser');
            if (targetSelect) {
                targetSelect.innerHTML = '<option value="">🎯 اختر الهدف...</option>';
                activeUsers.forEach(user => {
                    const userInfo = getUserDisplayInfo(user);
                    targetSelect.innerHTML += `<option value="@${user.username}">${userInfo.emoji} ${user.username} - ${userInfo.type}</option>`;
                });
            }

            // إنشاء قائمة المستخدمين المرئية
            updateUsersDisplay(users);

            console.log(`✅ تم تحميل ${users.length} مستخدم من الغرفة الفعلية`);

            // تحديث عدادات الإحصائيات
            const activeUsersElement = document.querySelector('.stats-active-users');
            const totalUsersElement = document.querySelector('.stats-total-users');
            if (activeUsersElement) {
                activeUsersElement.textContent = users.length;
            }
            // تحديث العدد الإجمالي أيضاً
            if (totalUsersElement) {
                totalUsersElement.textContent = users.length;
            }
        } else {
            console.error('فشل في الحصول على قائمة المستخدمين من الخادم', response.status);
            showToast('❌ فشل في الحصول على قائمة المستخدمين');
        }
    } catch (error) {
        console.error('خطأ في تحميل قائمة المستخدمين:', error);
        showToast('❌ خطأ في تحديث قائمة المستخدمين');
    }
}

// دالة تحديد معلومات عرض المستخدم
function getUserDisplayInfo(user) {
    let userType = 'مستخدم';
    let emoji = '👤';
    let bgClass = 'bg-light';

    // استخدام user_type من البيانات إذا كان متاحاً
    if (user.user_type) {
        switch (user.user_type) {
            case 'owner':
                userType = 'صاحب البوت';
                emoji = '👑';
                bgClass = 'bg-warning';
                break;
            case 'room_king':
                userType = 'صاحب الروم';
                emoji = '🔱';
                bgClass = 'bg-primary';
                break;
            case 'moderator':
                userType = 'مشرف';
                emoji = '👮‍♂️';
                bgClass = 'bg-success';
                break;
            default:
                userType = 'مستخدم';
                emoji = '👤';
                bgClass = 'bg-light';
        }
    }

    // التحقق من البوتات
    if (user.username.toLowerCase().includes('bot') || 
        user.id === '657a06ae5f8a5ec3ff16ec1b' || 
        user.username === 'NVuM_1') {
        userType = 'بوت';
        emoji = '🤖';
        bgClass = 'bg-info';
    }

    // مستخدمين VIP (حسب عدد الزيارات)
    else if (user.visit_count && user.visit_count > 100 && user.user_type === 'user') {
        userType = 'مستخدم VIP';
        emoji = '⭐';
        bgClass = 'bg-secondary';
    }

    return { type: userType, emoji: emoji, bgClass: bgClass };
}

// دالة تحديث عرض المستخدمين
function updateUsersDisplay(users) {
    // إضافة قسم عرض المستخدمين إذا لم يكن موجود
    let usersDisplaySection = document.getElementById('usersDisplaySection');
    if (!usersDisplaySection) {
        // سنضيف القسم في الـ HTML مباشرة
        return;
    }

    // إضافة زر التحديث في أعلى القسم
    let html = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5><i class="fas fa-users"></i> المستخدمين في الغرفة (${users.length})</h5>
            <button class="btn btn-primary btn-sm" onclick="refreshUsersList()">
                <i class="fas fa-sync-alt"></i> تحديث
            </button>
        </div>
        <div class="row">
    `;

    // ترتيب المستخدمين حسب النوع
    const sortedUsers = users.sort((a, b) => {
        const aInfo = getUserDisplayInfo(a);
        const bInfo = getUserDisplayInfo(b);

        // ترتيب الأولوية: مالك > صاحب روم > مشرف > بوت > VIP > عادي
        const priority = {
            'صاحب البوت': 6,
            'صاحب الروم': 5,
            'مشرف': 4,
            'بوت': 3,
            'مستخدم VIP': 2,
            'مستخدم': 1
        };

        return (priority[bInfo.type] || 0) - (priority[aInfo.type] || 0);
    });

    sortedUsers.forEach(user => {
        const userInfo = getUserDisplayInfo(user);
        const visitCount = user.visit_count || 0;
        const positionInfo = user.position ? 
            `📍 (${user.position.x.toFixed(1)}, ${user.position.z.toFixed(1)})` : 
            '📍 موقع غير معروف';

        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card ${userInfo.bgClass} text-white h-100 user-card" style="transition: all 0.3s; cursor: pointer;" 
                     onclick="selectUserForAction('${user.username}')">
                    <div class="card-body d-flex align-items-center">
                        <div class="me-3" style="font-size: 2rem;">
                            ${userInfo.emoji}
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="card-title mb-1 text-truncate">${user.username}</h6>
                            <small class="d-block">${userInfo.type}</small>
                            <small class="d-block">
                                <i class="fas fa-eye"></i> ${visitCount} زيارة
                            </small>
                            <small class="d-block text-success">
                                <i class="fas fa-circle" style="font-size: 8px;"></i> في الغرفة
                            </small>
                            <small class="d-block" title="${positionInfo}">
                                ${positionInfo}
                            </small>
                        </div>
                        <div class="text-end">
                            <button class="btn btn-sm btn-outline-light" onclick="event.stopPropagation(); quickActionUser('${user.username}')">
                                <i class="fas fa-cog"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    usersDisplaySection.innerHTML = html;
}

// دالة تحديث قائمة المستخدمين يدوياً
async function refreshUsersList() {
    showToast('🔄 جاري تحديث قائمة المستخدمين...');
    await loadUsersForSelection();
    showToast('✅ تم تحديث قائمة المستخدمين من الغرفة');
}

// دالة اختيار مستخدم للعمل
function selectUserForAction(username) {
    // تحديث جميع قوائم الاختيار
    const selects = ['userSelect', 'controlUsername', 'targetUser'];
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.value = `@${username}`;
        }
    });

    showToast(`تم اختيار المستخدم: ${username}`);
}

// دالة الإجراءات السريعة للمستخدم
function quickActionUser(username) {
    const actions = [
        { name: 'رقصة عشوائية', action: () => executeCommand(`عشوائي @${username}`) },
        { name: 'إحضار', action: () => executeCommand(`جيب @${username}`) },
        { name: 'معلومات', action: () => executeCommand(`معلومات @${username}`) }
    ];

    // عرض قائمة منبثقة بالإجراءات
    let actionHtml = `
        <div class="dropdown-menu show position-absolute" style="top: 0; left: 0; z-index: 1000;">
            <h6 class="dropdown-header">إجراءات ${username}</h6>
    `;

    actions.forEach(action => {
        actionHtml += `
            <button class="dropdown-item" onclick="event.stopPropagation(); ${action.action.toString()}; hideQuickActions();">
                ${action.name}
            </button>
        `;
    });

    actionHtml += '</div>';

    // عرض القائمة (هذا مثال بسيط، يمكن تحسينه)
    showToast(`إجراءات متاحة للمستخدم: ${username}`);
}

// تغيير محطة الراديو
async function changeRadioStation() {
    const radioUrl = document.getElementById('radioUrl').value.trim();
    
    if (!radioUrl) {
        showToast('❌ يرجى إدخال رابط محطة الراديو');
        return;
    }

    // التحقق من صحة الرابط
    if (!radioUrl.startsWith('http://') && !radioUrl.startsWith('https://')) {
        showToast('❌ يرجى استخدام رابط صحيح يبدأ بـ http:// أو https://');
        return;
    }

    try {
        const command = `راديو ${radioUrl}`;
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();
        
        if (data.success) {
            showToast(`📻 تم تشغيل محطة الراديو بنجاح!`);
            // مسح الحقل بعد النجاح
            document.getElementById('radioUrl').value = '';
        } else {
            showToast('❌ فشل في تشغيل محطة الراديو: ' + (data.error || 'خطأ غير معروف'));
        }
    } catch (error) {
        console.error('خطأ في تشغيل الراديو:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
    }
}

// تفعيل/إيقاف الرقص التلقائي للبوت
async function toggleBotAutoEmote() {
    const btn = document.getElementById('botAutoEmoteBtn');
    if (!btn) {
        console.error('لم يتم العثور على زر الرقص التلقائي');
        return;
    }

    console.log('تفعيل/إيقاف الرقص التلقائي، الحالة الحالية:', botAutoEmoteActive);

    if (!botAutoEmoteActive) {
        // تفعيل الرقص التلقائي
        try {
            const response = await fetch('/api/execute-command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'bot_dance' })
            });

            const data = await response.json();
            console.log('نتيجة تفعيل الرقص:', data);

            if (data.success) {
                botAutoEmoteActive = true;
                btn.innerHTML = '<i class="fas fa-robot"></i> إيقاف الرقص التلقائي للبوت';
                btn.className = 'btn btn-danger btn-sm me-2';
                showToast('✅ تم تفعيل الرقص التلقائي للبوت');
            } else {
                showToast('❌ فشل في تفعيل الرقص التلقائي: ' + (data.error || 'خطأ غير معروف'));
            }
        } catch (error) {
            console.error('خطأ في تفعيل الرقص التلقائي:', error);
            showToast('❌ خطأ في تفعيل الرقص التلقائي');
        }
    } else {
        // إيقاف الرقص التلقائي
        await stopBotAutoEmote();
    }
}

// دالة تنفيذ الأوامر العامة
async function executeCommand(command) {
    if (!command) {
        showToast('لا يوجد أمر للتنفيذ');
        return;
    }

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم تنفيذ الأمر: ${command}`);
            return true;
        } else {
            showToast('فشل في تنفيذ الأمر: ' + (data.error || 'خطأ غير معروف'));
            return false;
        }
    } catch (error) {
        console.error('خطأ في تنفيذ الأمر:', error);
        showToast('خطأ في الاتصال بالخادم');
        return false;
    }
}

// إيقاف الرقص التلقائي للبوت
async function stopBotAutoEmote() {
    try {
        const response = await fetch('/api/bot-auto-emote/stop', { method: 'POST' });
        const data = await response.json();

        botAutoEmoteActive = false;
        const btn = document.getElementById('botAutoEmoteBtn');
        btn.innerHTML = '<i class="fas fa-robot"></i> تفعيل الرقص التلقائي للبوت';
        btn.className = 'btn btn-success btn-sm me-2';
        showToast('تم إيقاف الرقص التلقائي للبوت');
    } catch (error) {
        showToast('خطأ في إيقاف الرقص التلقائي');
    }
}



// إيقاف جميع الرقصات
async function stopAllEmotes() {
    try {
        const response = await fetch('/api/stop-all-emotes', { method: 'POST' });
        const data = await response.json();

        botAutoEmoteActive = false;
        userRepeatedEmoteActive = false;

        const btn = document.getElementById('botAutoEmoteBtn');
        btn.innerHTML = '<i class="fas fa-robot"></i> تفعيل الرقص التلقائي للبوت';
        btn.className = 'btn btn-success btn-sm me-2';

        showToast('تم إيقاف جميع الرقصات');
    } catch (error) {
        showToast('فشل في إيقاف الرقصات');
    }
}

// تصفية الرقصات
function filterEmotes() {
    const searchTerm = document.getElementById('emoteSearchInput').value.toLowerCase();
    const emotesList = document.getElementById('emotesList');

    if (!searchTerm) {
        loadEmotesList(allEmotesData);
        return;
    }

    const filteredEmotes = allEmotesData.filter(emote => 
        emote.toLowerCase().includes(searchTerm)
    );

    loadEmotesList(filteredEmotes);
}

// مسح تصفية الرقصات
function clearEmoteFilter() {
    document.getElementById('emoteSearchInput').value = '';
    loadEmotesList(allEmotesData);
}

// إرسال ريأكشنز لجميع المستخدمين
async function sendReactionToAll(reactionType) {
    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: `send_reaction_all:${reactionType}` })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم إرسال ${reactionType} لجميع المستخدمين`);
            addToCommandLog(`إرسال ${reactionType} للجميع`, 'success');
        } else {
            showToast('فشل في إرسال الريأكشنز: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(`إرسال ${reactionType} للجميع`, 'error');
        }
    } catch (error) {
        console.error('خطأ في إرسال الريأكشنز:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(`إرسال ${reactionType} للجميع`, 'error');
    }
}

// عرض رسالة Toast
function showToast(message) {
    try {
        // البحث عن أو إنشاء عنصر Toast
        let toastElement = document.getElementById('copyToast');
        let toastBody = document.getElementById('toastBody');

        if (!toastElement) {
            // إنشاء Toast جديد إذا لم يكن موجود
            toastElement = document.createElement('div');
            toastElement.id = 'copyToast';
            toastElement.className = 'toast align-items-center text-white bg-primary border-0';
            toastElement.setAttribute('role', 'alert');
            toastElement.setAttribute('aria-live', 'assertive');
            toastElement.setAttribute('aria-atomic', 'true');
            toastElement.style.position = 'fixed';
            toastElement.style.top = '20px';
            toastElement.style.right = '20px';
            toastElement.style.zIndex = '9999';

            toastElement.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body" id="toastBody">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;

            document.body.appendChild(toastElement);
            toastBody = document.getElementById('toastBody');
        }

        if (toastBody) {
            toastBody.textContent = message;
        }

        // عرض Toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
        } else {
            // عرض بديل إذا لم يكن Bootstrap متاح
            toastElement.style.display = 'block';
            setTimeout(() => {
                toastElement.style.display = 'none';
            }, 3000);
        }
    } catch (error) {
        console.error('خطأ في عرض Toast:', error);
        // عرض تنبيه عادي كبديل
        alert(message);
    }
}

// البحث المتقدم عن الرقصات
function setupAdvancedSearch() {
    const searchInput = document.getElementById('emoteSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterEmotes();
            }
        });
    }
}

// إضافة مؤثرات بصرية للأزرار
function addButtonEffects() {
    const buttons = document.querySelectorAll('.btn-dance, .btn-custom');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.classList.add('glow');
        });

        button.addEventListener('mouseleave', function() {
            this.classList.remove('glow');
        });

        button.addEventListener('click', function() {
            this.classList.add('pulse');
            setTimeout(() => {
                this.classList.remove('pulse');
            }, 1000);
        });
    });
}

// تحديث الوقت الحقيقي لحالة البوت
async function updateBotStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        const statusElement = document.querySelector('.bot-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <i class="fas fa-circle text-success"></i> 
                ${data.message} - ${new Date(data.timestamp * 1000).toLocaleTimeString('ar-EG')}
            `;
        }
    } catch (error) {
        console.error('خطأ في تحديث حالة البوت:', error);
    }
}

// إضافة اختصارات لوحة المفاتيح
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + R للرقصة العشوائية
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            generateRandomNumber();
        }

        // Ctrl + S للبحث
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const searchInput = document.getElementById('emoteSearchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
}

// تحسين تجربة اللمس للأجهزة المحمولة
function setupTouchExperience() {
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');

        // تحسين حجم الأزرار للأجهزة المحمولة
        const style = document.createElement('style');
        style.textContent = `
            .touch-device .btn-dance {
                min-width: 50px;
                min-height: 40px;
                font-size: 13px;
            }
            .touch-device .btn-custom {
                padding: 12px 20px;
                font-size: 14px;
            }
        `;
        document.head.appendChild(style);
    }
}

// نسخ احتياطي للأوامر
function fallbackCopy(command) {
    const textArea = document.createElement('textarea');
    textArea.value = command;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    showToast(`تم نسخ الأمر: ${command}`);
}

// تشغيل جميع الوظائف عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // التأكد من تحميل الصفحة بالكامل
    setTimeout(() => {
        loadBotData();
        setupAdvancedSearch();
        addButtonEffects();
        addUserCardEffects(); // إضافة مؤثرات بطاقات المستخدمين
        setupKeyboardShortcuts();
        setupTouchExperience();
        setupCommandInput(); // إعداد واجهة الأوامر النصية
        setupSearchInputs(); // إعداد حقول البحث

        // تحديث حالة البوت كل 30 ثانية
        updateBotStatus();
    }, 100);

// تحديث معلومات أوقات الرقصات
async function updateEmoteTimingInfo() {
    try {
        const response = await fetch('/api/emote-timing');
        const data = await response.json();

        const timingDiv = document.getElementById('emoteTimingInfo');
        if (!timingDiv) return;

        let html = '';

        if (data.total_active > 0) {
            html += `<p><i class="fas fa-play-circle text-primary"></i> رقصات نشطة: ${data.total_active}</p>`;

            // عرض أول 3 رقصات نشطة
            const activeArray = Object.values(data.active_emotes).slice(0, 3);
            activeArray.forEach(emote => {
                const remainingMin = Math.floor(emote.remaining / 60);
                const remainingSec = Math.floor(emote.remaining % 60);
                const timeText = remainingMin > 0 ? `${remainingMin}د ${remainingSec}ث` : `${remainingSec}ث`;

                html += `<div class="small text-primary">
                    🎭 ${emote.username}: ${emote.emote}
                    <div class="progress mt-1 mb-2" style="height: 4px;">
                        <div class="progress-bar" style="width: ${emote.progress}%"></div>
                    </div>
                    <span class="text-muted">متبقي: ${timeText}</span>
                </div>`;
            });

            if (data.total_active > 3) {
                html += `<p class="small text-muted">... و${data.total_active - 3} رقصة أخرى</p>`;
            }
        }

        if (data.total_auto > 0) {
            html += `<p><i class="fas fa-sync-alt text-success"></i> رقصات تلقائية: ${data.total_auto}</p>`;

            // عرض أول 2 رقصة تلقائية
            const autoArray = Object.values(data.auto_emotes_stats).slice(0, 2);
            autoArray.forEach(stat => {
                html += `<div class="small text-success">
                    🔄 ${stat.username}: ${stat.emote} (${stat.loop_count} تكرار)
                </div>`;
            });
        }

        if (data.total_active === 0 && data.total_auto === 0) {
            html = '<p class="text-muted">😴 لا توجد رقصات نشطة حالياً</p>';
        }

        timingDiv.innerHTML = html;

    } catch (error) {
        console.error('خطأ في تحديث معلومات أوقات الرقصات:', error);
        const timingDiv = document.getElementById('emoteTimingInfo');
        if (timingDiv) {
            timingDiv.innerHTML = '<p class="text-danger">❌ خطأ في تحميل المعلومات</p>';
        }
    }
}

// دالة للحصول على مدة رقصة معينة
async function getEmoteDuration(emoteName) {
    try {
        const response = await fetch(`/api/emote-duration/${encodeURIComponent(emoteName)}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        return data;
    } catch (error) {
        console.error('خطأ في الحصول على مدة الرقصة:', error);
        return null;
    }
}

// تحديث معلومات أوقات الرقصات كل 5 ثوانِ
setInterval(updateEmoteTimingInfo, 5000);

// تحديث المعلومات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    updateEmoteTimingInfo();
});
    setInterval(updateBotStatus, 30000);

    // تحديث قائمة المستخدمين كل 15 ثانية لتبقى محدثة
    setInterval(loadUsersForSelection, 15000);

    // إضافة نص ترحيبي
    console.log('🤖 مرحباً بك في لوحة تحكم بوت Highrise المصري من فريق EDX!');
    console.log('💡 استخدم Ctrl+R للرقصة العشوائية، Ctrl+S للبحث');
    console.log('⌨️ استخدم Enter لإرسال الأوامر النصية');
});

// تثبيت المستخدم
async function freezeUser() {
    const username = document.getElementById('controlUsername').value;
    if (!username) {
        showToast('❌ يرجى اختيار المستخدم أولاً');
        return;
    }

    // استخدام اسم المستخدم كما هو بدون تعديل
    const finalCommand = username.startsWith('@') ? `ثبت ${username}` : `ثبت @${username}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: finalCommand,
                user_id: 'web_interface',
                username: 'WebInterface'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`🔒 تم إرسال أمر تثبيت ${username}`);
        } else {
            showToast(`❌ ${result.error}`);
        }
    } catch (error) {
        showToast(`❌ خطأ: ${error.message}`);
    }
}

// إلغاء تثبيت المستخدم
async function unfreezeUser() {
    const username = document.getElementById('controlUsername').value;
    if (!username) {
        showToast('❌ يرجى اختيار المستخدم أولاً');
        return;
    }

    // استخدام اسم المستخدم كما هو بدون تعديل
    const finalCommand = username.startsWith('@') ? `الغ ثبت ${username}` : `الغ ثبت @${username}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: finalCommand,
                user_id: 'web_interface',
                username: 'WebInterface'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`🔓 تم إرسال أمر إلغاء تثبيت ${username}`);
        } else {
            showToast(`❌ ${result.error}`);
        }
    } catch (error) {
        showToast(`❌ خطأ: ${error.message}`);
    }
}

// سجن المستخدم
async function jailUser() {
    const username = document.getElementById('controlUsername').value;
    if (!username) {
        showToast('❌ يرجى اختيار المستخدم أولاً');
        return;
    }

    // استخدام اسم المستخدم كما هو بدون تعديل
    const finalCommand = username.startsWith('@') ? `سجن ${username}` : `سجن @${username}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: finalCommand,
                user_id: 'web_interface', 
                username: 'WebInterface'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`⛓️ تم إرسال أمر سجن ${username}`);
        } else {
            showToast(`❌ ${result.error}`);
        }
    } catch (error) {
        showToast(`❌ خطأ: ${error.message}`);
    }
}

// دالة إلغاء تثبيت مستخدم
/*async function unfreezeUser() {
    const username = document.getElementById('controlUsername').value;
    if (!username) {
        showToast('❌ يرجى اختيار المستخدم أولاً');
        return;
    }

    try {
        const command = `الغ ثبت @${username}`;
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: command,
                user_id: 'web_interface',
                username: 'WebInterface'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`🔓 تم إرسال أمر إلغاء تثبيت ${username}`);
        } else {
            showToast(`❌ ${result.error}`);
        }
    } catch (error) {
        showToast(`❌ خطأ: ${error.message}`);
    }
}

// إرسال أمر نصي مباشر*/
async function sendCommand() {
    const commandInput = document.getElementById('commandInput');
    const command = commandInput.value.trim();

    if (!command) {
        showToast('يرجى كتابة أمر أولاً');
        return;
    }

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم إرسال الأمر: ${command}`);
            addToCommandLog(command, 'success');
            commandInput.value = ''; // مسح الحقل
        } else {
            showToast('فشل في إرسال الأمر: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(command, 'error');
        }
    } catch (error) {
        console.error('خطأ في إرسال الأمر:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(command, 'error');
    }
}

// إرسال أمر سريع
async function sendQuickCommand(command) {
    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم تنفيذ الأمر: ${command}`);
            addToCommandLog(command, 'success');
        } else {
            showToast('فشل في تنفيذ الأمر: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(command, 'error');
        }
    } catch (error) {
        console.error('خطأ في تنفيذ الأمر:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(command, 'error');
    }
}

// إرسال أمر رقص للجميع
async function sendDanceAllCommand() {
    const danceNumber = document.getElementById('danceNumber').value;

    if (!danceNumber || danceNumber < 1 || danceNumber > 183) {
        showToast('يرجى إدخال رقم رقصة صحيح (1-183)');
        return;
    }

    const command = `رقص_الكل ${danceNumber}`;
    await sendQuickCommand(command);
}

// إرسال أمر رقص لمستخدم محدد
async function sendUserDanceCommand() {
    const danceNumber = document.getElementById('danceNumber').value;
    const targetUser = document.getElementById('targetUser').value.trim();

    if (!danceNumber || danceNumber < 1 || danceNumber > 183) {
        showToast('يرجى إدخال رقم رقصة صحيح (1-183)');
        return;
    }

    if (!targetUser) {
        showToast('يرجى إدخال اسم المستخدم');
        return;
    }

    const command = `رقص ${danceNumber} @${targetUser}`;
    await sendQuickCommand(command);
}

// إضافة أمر لسجل الأوامر
function addToCommandLog(command, status) {
    const commandLog = document.getElementById('commandLog');
    const timestamp = new Date().toLocaleTimeString('ar-EG');
    const statusIcon = status === 'success' ? '✅' : '❌';
    const statusColor = status === 'success' ? 'text-success' : 'text-danger';

    const logEntry = document.createElement('div');
    logEntry.className = `mb-1 ${statusColor}`;
    logEntry.innerHTML = `
        <small>
            <span class="text-muted">[${timestamp}]</span> 
            ${statusIcon} ${command}
        </small>
    `;

    commandLog.appendChild(logEntry);
    commandLog.scrollTop = commandLog.scrollHeight; // التمرير لأسفل

    // الاحتفاظ بآخر 20 أمر فقط
    const entries = commandLog.children;
    if (entries.length > 20) {
        commandLog.removeChild(entries[0]);
    }
}

// إضافة استماع لضغطة Enter في حقل الأمر
function setupCommandInput() {
    const commandInput = document.getElementById('commandInput');
    if (commandInput) {
        commandInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendCommand();
            }
        });
        console.log('✅ تم إعداد حقل الأوامر النصية');
    } else {
        console.warn('⚠️ عنصر commandInput غير موجود في الصفحة');
    }
}

// وظائف إضافية للمطورين
window.botInterface = {
    copyCommand,
    loadBotData,
    toggleBotAutoEmote,
    generateRandomNumber,
    sendCommand,
    sendQuickCommand
};

// وظائف أيقونة المعلومات والملابس المدمجة
function toggleAboutIcon() {
    const infoIcon = document.getElementById('infoIcon');
    const outfitIcon = document.getElementById('outfitIcon');
    const aboutBtn = document.getElementById('aboutBtn');

    // التحقق من وجود العناصر قبل استخدامها
    if (!infoIcon || !outfitIcon || !aboutBtn) {
        console.warn('بعض العناصر المطلوبة غير موجودة في الصفحة');
        return;
    }

    if (infoIcon.classList.contains('show') || outfitIcon.classList.contains('show')) {
        // إخفاء جميع الأيقونات
        infoIcon.classList.remove('show');
        outfitIcon.classList.remove('show');
        aboutBtn.style.transform = 'scale(1) rotate(0deg)';
    } else {
        // إظهار جميع الأيقونات مع انيميشن
        infoIcon.classList.add('show');
        outfitIcon.classList.add('show');
        aboutBtn.style.transform = 'scale(0.9) rotate(45deg)';

        // تأثير صوتي بصري
        aboutBtn.style.background = 'linear-gradient(45deg, #ffa500, #ff7f00)';
        setTimeout(() => {
            aboutBtn.style.background = 'linear-gradient(45deg, #ff8c00, #ffa500)';
        }, 200);
    }
}

// فتح صفحة الملابس
function openOutfitPage() {
    // إخفاء جميع الأيقونات أولاً
    const infoIcon = document.getElementById('infoIcon');
    const outfitIcon = document.getElementById('outfitIcon');
    const aboutBtn = document.getElementById('aboutBtn');

    if (infoIcon && outfitIcon) {
        infoIcon.classList.remove('show');
        outfitIcon.classList.remove('show');
        aboutBtn.style.transform = 'scale(1) rotate(0deg)';
    }

    // فتح صفحة الملابس في نافذة جديدة أو نفس النافذة
    window.open('/outfits', '_blank');

    // تأثير بصري للزر الرئيسي
    if (aboutBtn) {
        aboutBtn.style.background = 'linear-gradient(45deg, #e91e63, #f06292)';
        setTimeout(() => {
            aboutBtn.style.background = 'linear-gradient(45deg, #ff8c00, #ffa500)';
        }, 300);
    }
}

// فتح نافذة معلومات البوت
function openAboutModal() {
    // إخفاء جميع الأيقونات أولاً
    const infoIcon = document.getElementById('infoIcon');
    const outfitIcon = document.getElementById('outfitIcon');
    const aboutBtn = document.getElementById('aboutBtn');

    infoIcon.classList.remove('show');
    outfitIcon.classList.remove('show');
    aboutBtn.style.transform = 'scale(1) rotate(0deg)';

    // فتح النافذة
    const modal = new bootstrap.Modal(document.getElementById('aboutModal'));
    modal.show();

    // تأثير بصري للزر الرئيسي
    aboutBtn.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
    setTimeout(() => {
        aboutBtn.style.background = 'linear-gradient(45deg, #ff8c00, #ffa500)';
    }, 300);
}

// فتح نافذة أوامر الهاك
function openHackControlModal() {
    const modal = new bootstrap.Modal(document.getElementById('hackControlModal'));
    modal.show();

    // تحديث قائمة المستخدمين والرقصات
    updateHackTargets();
    updateHackEmotes();

    // إضافة تأثير صوتي للهاك
    addHackStatusMessage("🔴 تم تفعيل وضع الهاك...");
    addHackStatusMessage("⚡ البحث عن الأهداف المتاحة...");
    addHackStatusMessage("💀 نظام الاختراق جاهز للتنفيذ!");
}

// تحديث قائمة أهداف الهاك
function updateHackTargets() {
    const select = document.getElementById('hackTargetUser');
    if (!select) return;

    select.innerHTML = '<option value="">💀 اختر المستخدم المراد اختراقه...</option>';

    if (currentUsers && currentUsers.length > 0) {
        currentUsers.forEach(user => {
            const option = document.createElement('option');
            option.value = user.username;
            option.textContent = `🎯 ${user.username} (${user.user_type})`;
            select.appendChild(option);
        });
    }
}



// تحديث قائمة الرقصات للهاك
function updateHackEmotes() {
    const select = document.getElementById('hackEmoteSelect');
    if (!select) return;

    select.innerHTML = '<option value="">💃 اختر رقصة للسيطرة...</option>';

    if (emotesList && emotesList.length > 0) {
        // أهم الرقصات للهاك
        const hackEmotes = [
            'emote-teleporting', 'emote-death2', 'emote-zombiedance', 
            'emote-gravity', 'emote-hero', 'emote-villain',
            'dance-tiktok9', 'dance-orangejustice', 'idle-loop-sitfloor'
        ];

        hackEmotes.forEach((emoteName, index) => {
            const option = document.createElement('option');
            option.value = emoteName;
            option.textContent = `🎭 ${emoteName}`;
            select.appendChild(option);
        });

        // إضافة باقي الرقصات
        emotesList.slice(0, 20).forEach((emote, index) => {
            if (!hackEmotes.includes(emote.name)) {
                const option = document.createElement('option');
                option.value = emote.name;
                option.textContent = `💃 ${emote.name}`;
                select.appendChild(option);
            }
        });
    }
}

// تنفيذ أوامر الهاك
function executeHackCommand(command) {
    const targetUser = document.getElementById('hackTargetUser').value;

    if (!targetUser) {
        addHackStatusMessage("❌ خطأ: لم يتم تحديد هدف!");
        return;
    }

    addHackStatusMessage(`🎯 الهدف المحدد: ${targetUser}`);
    addHackStatusMessage(`⚡ تنفيذ الأمر: ${command}`);

    let commandToSend = '';

    switch(command) {
        case 'dance':
            const selectedEmote = document.getElementById('hackEmoteSelect').value;
            if (!selectedEmote) {
                addHackStatusMessage("❌ خطأ: لم يتم تحديد رقصة!");
                return;
            }
            commandToSend = `هاك_رقص @${targetUser} ${selectedEmote}`;
            addHackStatusMessage(`🎭 اختراق نظام الرقص: ${selectedEmote}`);
            break;

        case 'teleport_to_bot':
            commandToSend = `جيب @${targetUser}`;
            addHackStatusMessage(`🚀 سحب الهدف إلى موقع البوت...`);
            break;

        case 'teleport_to_coords':
            const x = document.getElementById('hackPosX').value || 0;
            const y = document.getElementById('hackPosY').value || 0;
            const z = document.getElementById('hackPosZ').value || 0;
            commandToSend = `هاك_نقل @${targetUser} ${x} ${y} ${z}`;
            addHackStatusMessage(`📍 نقل إلى إحداثيات: (${x}, ${y}, ${z})`);
            break;

        case 'freeze':
            commandToSend = `ثبت @${targetUser}`;
            addHackStatusMessage(`🔒 تجميد الهدف في مكانه...`);
            break;

        case 'jail':
            commandToSend = `سجن @${targetUser}`;
            addHackStatusMessage(`⛓️ نقل الهدف إلى السجن...`);
            break;

        case 'stop_emote':
            commandToSend = `ايقاف @${targetUser}`;
            addHackStatusMessage(`⏹️ إيقاف جميع التأثيرات...`);
            break;
    }

    if (commandToSend) {
        addHackStatusMessage(`📡 إرسال الأمر: ${commandToSend}`);
        sendCommand(commandToSend);
        addHackStatusMessage(`✅ تم اختراق المستخدم @${targetUser} بنجاح!`);
        addHackStatusMessage(`💀 عملية الاختراق مكتملة!`);
    }
}

// إضافة رسالة لشاشة الهاك
function addHackStatusMessage(message) {
    const display = document.getElementById('hackStatusDisplay');
    if (display) {
        const timestamp = new Date().toLocaleTimeString();
        display.innerHTML += `<span style="color: #666;">[${timestamp}]</span> ${message}<br>`;
        display.scrollTop = display.scrollHeight;
    }
}

// إضافة تأثيرات للأيقونات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تأثير الظهور التدريجي للأيقونة الرئيسية
    const aboutBtn = document.getElementById('aboutBtn');
    if (aboutBtn) {
        setTimeout(() => {
            aboutBtn.style.opacity = '0';
            aboutBtn.style.transform = 'scale(0)';
            aboutBtn.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';

            setTimeout(() => {
                aboutBtn.style.opacity = '1';
                aboutBtn.style.transform = 'scale(1)';
            }, 1000);
        }, 100);
    }

    // إضافة استماع للنقر خارج الأيقونات لإخفائها
    document.addEventListener('click', function(e) {
        const container = document.querySelector('.floating-info-container');
        const infoIcon = document.getElementById('infoIcon');
        const outfitIcon = document.getElementById('outfitIcon');
        const aboutBtn = document.getElementById('aboutBtn');

        if (container && !container.contains(e.target) && (infoIcon.classList.contains('show') || outfitIcon.classList.contains('show'))) {
            infoIcon.classList.remove('show');
            outfitIcon.classList.remove('show');
            aboutBtn.style.transform = 'scale(1) rotate(0deg)';
        }
    });

    // منع انتشار النقر داخل الحاوي
    const container = document.querySelector('.floating-info-container');
    if (container) {
        container.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});

// دالة البحث في قائمة المستخدمين
function filterUsersDisplay() {
    const searchTerm = document.getElementById('userSearchInput').value.toLowerCase();
    const userCards = document.querySelectorAll('.user-card');

    userCards.forEach(card => {
        const username = card.querySelector('.card-title').textContent.toLowerCase();
        const userType = card.querySelector('small').textContent.toLowerCase();

        if (username.includes(searchTerm) || userType.includes(searchTerm)) {
            card.closest('.col-md-6').style.display = 'block';
        } else {
            card.closest('.col-md-6').style.display = 'none';
        }
    });
}

// إضافة الدوال المفقودة
function clearEmoteFilter() {
    const searchInput = document.getElementById('emoteSearchInput');
    if (searchInput) {
        searchInput.value = '';
        loadEmotesList(allEmotesData);
    }
}

// دالة البحث عن رقصة
function searchDance() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const searchTerm = searchInput.value.trim();
        if (searchTerm) {
            executeCommand(`ابحث رقصة ${searchTerm}`);
        } else {
            showToast('يرجى كتابة اسم الرقصة للبحث');
        }
    }
}

// دالة تنفيذ رقصة جوست
async function executeGhostDance() {
    await executeCommand('جوست');
}

// دالة تنفيذ رقصة نوم
async function executeSleepDance() {
    await executeCommand('نوم');
}

// دالة تنفيذ رقصة عبدو (استرخاء)
async function executeRelaxDance() {
    await executeCommand('عبدو');
}

// إضافة مؤثرات للبطاقات
function addUserCardEffects() {
    document.addEventListener('mouseover', function(e) {
        if (e.target.closest('.user-card')) {
            e.target.closest('.user-card').style.transform = 'scale(1.02)';
            e.target.closest('.user-card').style.boxShadow = '0 8px 16px rgba(0,0,0,0.3)';
        }
    });

    document.addEventListener('mouseout', function(e) {
        if (e.target.closest('.user-card')) {
            e.target.closest('.user-card').style.transform = 'scale(1)';
            e.target.closest('.user-card').style.boxShadow = '';
        }
    });
}

// البحث عند الضغط على Enter (إذا كان العنصر موجود)
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchDance();
                }
            });
        }

        // إعداد حقل ID المستخدم
        setupUserIdInput();

        // دالة إعداد حقول البحث
function setupSearchInputs() {
    // إضافة استماع لحقل الرسائل العامة
    const publicMessageInput = document.getElementById('publicMessageInput');
    if (publicMessageInput) {
        publicMessageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendPublicMessage();
            }
        });
        console.log('✅ تم إعداد حقل الرسائل العامة');
    }

    // إضافة استماع لبحث المستخدمين
    const userSearchInput = document.getElementById('userSearchInput');
    if (userSearchInput) {
        userSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterUsersDisplay();
            }
        });
    }

    // إضافة استماع للبحث في الرقصات
    const emoteSearchInput = document.getElementById('emoteSearchInput');
    if (emoteSearchInput) {
        emoteSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterEmotes();
            }
        });
    }

    // البحث العام إذا كان موجود
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDance();
            }
        });
    }
}
// تحديث حالة الاتصال
async function updateConnectionStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // تحديث مؤشر الحالة حسب استجابة الخادم
        updateStatusIndicator(data.success);

        // تحديث حالة البوت في النافبار
        const botStatus = document.getElementById('botStatus');
        if (botStatus) {
            if (data.success) {
                botStatus.innerHTML = '<i class="fas fa-check-circle text-success"></i> البوت متصل ونشط';
            } else {
                botStatus.innerHTML = '<i class="fas fa-exclamation-triangle text-warning"></i> البوت غير متصل';
            }
        }

    } catch (error) {
        console.error('خطأ في التحقق من حالة الاتصال:', error);
        updateStatusIndicator(false);

        // تحديث حالة البوت عند الخطأ
        const botStatus = document.getElementById('botStatus');
        if (botStatus) {
            botStatus.innerHTML = '<i class="fas fa-times-circle text-danger"></i> خطأ في الاتصال';
        }
    }
}

// إصلاح مشكلة addEventListener
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 مرحباً بك في لوحة تحكم بوت Highrise المصري من فريق EDX!');
    console.log('💡 استخدم Ctrl+R للرقصة العشوائية، Ctrl+S للبحث');
    console.log('⌨️ استخدم Enter لإرسال الأوامر النصية');

    // التأكد من تحميل الصفحة بالكامل
    setTimeout(() => {
        try {
            loadBotData();
            setupAdvancedSearch();
            addButtonEffects();
            addUserCardEffects();
            setupKeyboardShortcuts();
            setupTouchExperience();
            setupCommandInput();
            setupSearchInputs();

            // تحديث حالة البوت كل 30 ثانية
            updateBotStatus();
            setInterval(updateBotStatus, 30000);

            // تحديث قائمة المستخدمين كل 15 ثانية
            setInterval(loadUsersForSelection, 15000);

            console.log('✅ تم تحميل جميع المكونات بنجاح');
        } catch (error) {
            console.error('❌ خطأ في تحميل المكونات:', error);
        }
    }, 100);
});

// تثبيت المستخدم
async function freezeUser() {
    const username = document.getElementById('controlUsername').value;
    if (!username) {
        showToast('❌ يرجى اختيار المستخدم أولاً');
        return;
    }

    // استخدام اسم المستخدم كما هو بدون تعديل
    const finalCommand = username.startsWith('@') ? `ثبت ${username}` : `ثبت @${username}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: finalCommand,
                user_id: 'web_interface',
                username: 'WebInterface'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`🔒 تم إرسال أمر تثبيت ${username}`);
        } else {
            showToast(`❌ ${result.error}`);
        }
    } catch (error) {
        showToast(`❌ خطأ: ${error.message}`);
    }
}

// سجن المستخدم
async function jailUser() {
    const username = document.getElementById('controlUsername').value;
    if (!username) {
        showToast('❌ يرجى اختيار المستخدم أولاً');
        return;
    }

    // استخدام اسم المستخدم كما هو بدون تعديل
    const finalCommand = username.startsWith('@') ? `سجن ${username}` : `سجن @${username}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: finalCommand,
                user_id: 'web_interface', 
                username: 'WebInterface'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`⛓️ تم إرسال أمر سجن ${username}`);
        } else {
            showToast(`❌ ${result.error}`);
        }
    } catch (error) {
        showToast(`❌ خطأ: ${error.message}`);
    }
}

// دالة عرض معلومات الأعضاء
async function showMembersInfo() {
    try {
        // الحصول على المستخدمين في الغرفة الحالية
        const roomResponse = await fetch('/api/room-users');
        const roomData = await roomResponse.json();

        // الحصول على إجمالي المستخدمين من قاعدة البيانات
        const totalResponse = await fetch('/api/users');
        const totalData = await totalResponse.json();

        if (roomData.success && totalData.success) {
            const currentUsers = roomData.users.length;
            const totalUsers = totalData.users.length;

            showToast(`👥 المتصلين الآن: ${currentUsers} | إجمالي الزوار: ${totalUsers}`);
        } else {
            showToast('❌ فشل في الحصول على معلومات الأعضاء');
        }
    } catch (error) {
        console.error('خطأ في عرض معلومات الأعضاء:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
    }
}

// دالة وديني
async function teleportUserToTarget(targetUsername) {
    const command = `وديني @${targetUsername}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم تنفيذ الأمر: ${command}`);
            addToCommandLog(command, 'success');
        } else {
            showToast('فشل في تنفيذ الأمر: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(command, 'error');
        }
    } catch (error) {
        console.error('خطأ في تنفيذ الأمر:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(command, 'error');
    }
}

// دالة الحصول على ID مستخدم
async function getUserId() {
    const userIdInput = document.getElementById('userIdInput');
    const username = userIdInput.value.trim();

    if (!username) {
        showToast('❌ يرجى كتابة اسم المستخدم أولاً');
        return;
    }

    // إزالة @ إذا كانت موجودة
    const cleanUsername = username.replace('@', '');
    const command = `اي دي ${cleanUsername}`;

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`🆔 تم إرسال أمر الحصول على ID للمستخدم: ${cleanUsername}`);
            addToCommandLog(command, 'success');
            userIdInput.value = ''; // مسح الحقل
        } else {
            showToast('فشل في الحصول على ID: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(command, 'error');
        }
    } catch (error) {
        console.error('خطأ في الحصول على ID:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(command, 'error');
    }
}

// إضافة استماع لضغطة Enter في حقل ID المستخدم
function setupUserIdInput() {
    const userIdInput = document.getElementById('userIdInput');
    if (userIdInput) {
        userIdInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                getUserId();
            }
        });
    }
}

// وظائف فك الضغط
async function extractZipFile(zipPath, extractTo = null, password = null) {
    try {
        const response = await fetch('/api/extract-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                zip_path: zipPath,
                extract_to: extractTo,
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`✅ تم فك الضغط بنجاح - ${data.files_extracted} ملف`);
            console.log('تم فك الضغط إلى:', data.extract_path);
            return data;
        } else {
            showToast('❌ فشل في فك الضغط: ' + data.error);
            return null;
        }
    } catch (error) {
        console.error('خطأ في فك الضغط:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
        return null;
    }
}

async function createZipFile(sourcePath, zipPath, compressionLevel = 6) {
    try {
        const response = await fetch('/api/create-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_path: sourcePath,
                zip_path: zipPath,
                compression_level: compressionLevel
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`✅ تم إنشاء ملف ZIP - ${data.files_added} ملف (${data.size})`);
            return data;
        } else {
            showToast('❌ فشل في إنشاء ZIP: ' + data.error);
            return null;
        }
    } catch (error) {
        console.error('خطأ في إنشاء ZIP:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
        return null;
    }
}

async function listZipContents(zipPath) {
    try {
        const response = await fetch('/api/list-zip-contents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zip_path: zipPath })
        });

        const data = await response.json();

        if (data.success) {
            console.log('محتويات ZIP:', data);
            showToast(`📋 الملف يحتوي على ${data.total_files} ملف (${data.total_size})`);
            return data;
        } else {
            showToast('❌ فشل في قراءة محتويات ZIP: ' + data.error);
            return null;
        }
    } catch (error) {
        console.error('خطأ في قراءة محتويات ZIP:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
        return null;
    }
}

async function validateZipFile(zipPath) {
    try {
        const response = await fetch('/api/validate-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zip_path: zipPath })
        });

        const data = await response.json();

        if (data.success) {
            if (data.is_valid) {
                showToast(`✅ ${data.status} - تم فحص ${data.tested_files} ملف`);
            } else {
                showToast(`⚠️ ${data.status}`);
                console.log('الملفات التالفة:', data.corrupt_files);
            }
            return data;
        } else {
            showToast('❌ فشل في فحص ZIP: ' + data.error);
            return null;
        }
    } catch (error) {
        console.error('خطأ في فحص ZIP:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
        return null;
    }
}

// وظيفة مساعدة لاختبار فك الضغط
function testZipExtraction() {
    const zipPath = prompt('أدخل مسار ملف ZIP للاختبار:');
    if (zipPath) {
        extractZipFile(zipPath);
    }
}

// Dance Command

async function createDanceCommand() {
    const command = document.getElementById('danceName').value.trim();
    const emote = document.getElementById('danceEmote').value.trim();
    const message = document.getElementById('danceMessage').value.trim();
    const permissions = document.getElementById('dancePermissions').value;

    if (!command || !emote) {
        showToast('❌ يرجى ملء اسم الأمر والرقصة');
        return;
    }

    try {
        const response = await fetch('/api/create-dance-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: command,
                emote: emote,
                message: message,
                permissions: permissions
            })
        });

        const data = await response.json();

if (data.success) {
            showToast(`✅ تم إنشاء الأمر بنجاح: ${command}`);
            // clearForm()
        } else {
            showToast('❌ فشل في إنشاء الأمر: ' + (data.error || 'خطأ غير معروف'));
        }
    } catch (error) {
        console.error('خطأ في إنشاء الأمر:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
    }
}

// Navigation Command
async function createNavCommand() {
    const command = document.getElementById('navName').value.trim();
    const x = document.getElementById('navX').value;
    const y = document.getElementById('navY').value;
    const z = document.getElementById('navZ').value;
    const message = document.getElementById('navMessage').value.trim();
    const permissions = document.getElementById('navPermissions').value;

    if (!command || !x || !y || !z) {
        showToast('❌ يرجى ملء اسم الأمر والإحداثيات');
        return;
    }

    try {
        const response = await fetch('/api/create-nav-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: command,
                x: x,
                y: y,
                z: z,
                message: message,
                permissions: permissions
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`✅ تم إنشاء الأمر بنجاح: ${command}`);
            // clearForm()
        } else {
            showToast('❌ فشل في إنشاء الأمر: ' + (data.error || 'خطأ غير معروف'));
        }
    } catch (error) {
        console.error('خطأ في إنشاء الأمر:', error);
        showToast('❌ خطأ في الاتصال بالخادم');
    }
}

        // متغير لحفظ بيانات الرقصات المحملة
        let globalEmotesData = null;

        // تحميل قائمة الرقصات
        async function loadEmotes() {
            try {
                console.log('🔄 جاري تحميل قائمة الرقصات...');
                const response = await fetch('/api/emotes');
                const data = await response.json();

                // حفظ البيانات للاستخدام في دوال أخرى
                globalEmotesData = data;

                // إضافة الرقصات إلى القائمة
                    const emotesList = data.emotes_list;
                    const danceEmoteSelect = document.getElementById('danceEmote');
                    danceEmoteSelect.innerHTML = '<option value="">💃 اختر رقصة...</option>';
                    // إضافة الرقصات إلى القائمة
                    emotesList.forEach((emote, index) => {
                        const option = document.createElement('option');
                        option.value = emote;
                        const emoteNumber = index + 1;
                        option.textContent = `${emoteNumber}. ${emote}`;
                        danceEmoteSelect.appendChild(option);
                    });
            } catch (error) {
                console.error('خطأ في تحميل قائمة الرقصات:', error);
            }
        }

        // معاينة الرقصة المختارة
        function previewDance() {
            const selectedEmote = document.getElementById('danceEmote').value;
            const previewDiv = document.getElementById('dancePreview');

            if (selectedEmote) {
                // البحث عن رقم الرقصة
                let emoteNumber = 'غير معروف';
                if (globalEmotesData && globalEmotesData.emotes_list && Array.isArray(globalEmotesData.emotes_list)) {
                    const index = globalEmotesData.emotes_list.indexOf(selectedEmote);
                    if (index !== -1) {
                        emoteNumber = index + 1;
                    }
                }
                previewDiv.innerHTML = `<i class="fas fa-music"></i> الرقصة المختارة: <strong>#${emoteNumber} - ${selectedEmote}</strong>`;
                previewDiv.className = 'alert alert-success';
            } else {
                previewDiv.innerHTML = '<i class="fas fa-info-circle"></i> اختر رقصة لمعاينة اسمها ورقمها';
                previewDiv.className = 'alert alert-info';
            }
        }
// إرسال رسالة عامة
async function sendPublicMessage() {
    const publicMessageInput = document.getElementById('publicMessageInput');
    const message = publicMessageInput.value.trim();

    if (!message) {
        showToast('يرجى كتابة رسالة أولاً');
        return;
    }

    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: `say ${message}` })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم إرسال الرسالة العامة: ${message}`);
            addToCommandLog(`رسالة: ${message}`, 'success');
            publicMessageInput.value = ''; // مسح الحقل
        } else {
            showToast('فشل في إرسال الرسالة: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(`رسالة: ${message}`, 'error');
        }
    } catch (error) {
        console.error('خطأ في إرسال الرسالة:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(`رسالة: ${message}`, 'error');
    }
}

// إرسال رسالة سريعة
async function sendQuickPublicMessage(message) {
    try {
        const response = await fetch('/api/execute-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: `say ${message}` })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`تم إرسال الرسالة: ${message}`);
            addToCommandLog(`رسالة سريعة: ${message}`, 'success');
        } else {
            showToast('فشل في إرسال الرسالة: ' + (data.error || 'خطأ غير معروف'));
            addToCommandLog(`رسالة سريعة: ${message}`, 'error');
        }
    } catch (error) {
        console.error('خطأ في إرسال الرسالة السريعة:', error);
        showToast('خطأ في الاتصال بالخادم');
        addToCommandLog(`رسالة سريعة: ${message}`, 'error');
    }
}
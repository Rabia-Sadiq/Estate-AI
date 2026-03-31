/**
 * Estate-AI — Shared Auth + Utilities
 * Used by all pages. Handles login state, modals, and add-property flow.
 */

const API = 'http://127.0.0.1:8000';

// ── Auth helpers ─────────────────────────────────────────────────────────────
const Auth = {
  get() {
    try { return JSON.parse(localStorage.getItem('estateai_user') || 'null'); }
    catch { return null; }
  },
  set(user) { localStorage.setItem('estateai_user', JSON.stringify(user)); },
  clear()   { localStorage.removeItem('estateai_user'); },
  isLoggedIn() { return !!this.get(); }
};

// ── Price formatter ───────────────────────────────────────────────────────────
function fmtPrice(pkr) {
  if (!pkr) return '';
  pkr = parseFloat(pkr);
  if (pkr >= 10000000) return (pkr / 10000000).toFixed(2).replace(/\.?0+$/, '') + ' Crore';
  if (pkr >= 100000)   return (pkr / 100000).toFixed(1).replace(/\.0$/, '') + ' Lakh';
  return pkr.toLocaleString();
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = `fixed bottom-6 right-6 z-[9999] px-5 py-3 rounded-xl text-sm font-semibold shadow-xl transition-all
    ${type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-500 text-white'}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// ── Inject global auth modal + add-property modal into every page ─────────────
function injectModals() {
  const html = `
  <!-- ══════════════ AUTH MODAL ══════════════ -->
  <div id="auth-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-[9990] flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl w-full max-w-md shadow-2xl overflow-hidden">
      <!-- Tabs -->
      <div class="flex border-b border-gray-100">
        <button onclick="switchAuthTab('login')" id="tab-login"
          class="flex-1 py-4 text-sm font-bold tracking-wide border-b-2 border-emerald-600 text-emerald-700 transition-all">
          Sign In
        </button>
        <button onclick="switchAuthTab('signup')" id="tab-signup"
          class="flex-1 py-4 text-sm font-bold tracking-wide border-b-2 border-transparent text-gray-400 transition-all">
          Create Account
        </button>
      </div>

      <!-- Login Form -->
      <div id="auth-login" class="p-8">
        <div class="text-center mb-6">
          <div class="w-14 h-14 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-3">
            <span class="text-2xl">🏠</span>
          </div>
          <h2 class="text-xl font-bold text-gray-900">Welcome back</h2>
          <p class="text-sm text-gray-500 mt-1">Use your phone number to sign in</p>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Phone Number *</label>
            <input id="li-phone" type="tel" placeholder="0300-1234567"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Your Name *</label>
            <input id="li-name" type="text" placeholder="Ahmed Khan"
              onkeydown="if(event.key==='Enter')doLogin()"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <button onclick="doLogin()"
            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-sm transition-all active:scale-95">
            Sign In →
          </button>
          <p class="text-xs text-gray-400 text-center">No password needed — your phone is your identity</p>
        </div>
      </div>

      <!-- Signup Form -->
      <div id="auth-signup" class="p-8 hidden">
        <div class="text-center mb-6">
          <div class="w-14 h-14 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-3">
            <span class="text-2xl">✨</span>
          </div>
          <h2 class="text-xl font-bold text-gray-900">Join Estate-AI</h2>
          <p class="text-sm text-gray-500 mt-1">Create your free account</p>
        </div>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">First Name *</label>
              <input id="su-fname" type="text" placeholder="Ahmed"
                class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Last Name</label>
              <input id="su-lname" type="text" placeholder="Khan"
                class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Phone Number *</label>
            <input id="su-phone" type="tel" placeholder="0300-1234567"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Email (optional)</label>
            <input id="su-email" type="email" placeholder="ahmed@email.com"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">I am a</label>
            <div class="grid grid-cols-2 gap-2">
              <label class="flex items-center gap-2 px-4 py-3 rounded-xl border border-gray-200 cursor-pointer hover:border-emerald-400 transition-all has-[:checked]:border-emerald-500 has-[:checked]:bg-emerald-50">
                <input type="radio" name="su-role" value="buyer" checked class="accent-emerald-600"/>
                <span class="text-sm font-semibold text-gray-700">Buyer</span>
              </label>
              <label class="flex items-center gap-2 px-4 py-3 rounded-xl border border-gray-200 cursor-pointer hover:border-emerald-400 transition-all has-[:checked]:border-emerald-500 has-[:checked]:bg-emerald-50">
                <input type="radio" name="su-role" value="seller" class="accent-emerald-600"/>
                <span class="text-sm font-semibold text-gray-700">Seller</span>
              </label>
            </div>
          </div>
          <button onclick="doSignup()"
            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-sm transition-all active:scale-95">
            Create Account ✨
          </button>
        </div>
      </div>

      <button onclick="closeAuthModal()"
        class="absolute top-4 right-4 w-8 h-8 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200 flex items-center justify-center text-lg font-bold transition-all">
        ×
      </button>
    </div>
  </div>

  <!-- ══════════════ ADD PROPERTY MODAL ══════════════ -->
  <div id="add-prop-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-[9990] flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl w-full max-w-2xl shadow-2xl max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between p-6 border-b border-gray-100 sticky top-0 bg-white rounded-t-3xl z-10">
        <div>
          <h2 class="text-xl font-bold text-gray-900">List Your Property</h2>
          <p class="text-sm text-gray-500">Fill in the details to get it live</p>
        </div>
        <button onclick="closeAddPropModal()" class="w-9 h-9 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200 flex items-center justify-center text-xl font-bold transition-all">×</button>
      </div>
      <form id="global-add-form" class="p-6 space-y-5" onsubmit="submitAddProperty(event)">
        <div>
          <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Property Title *</label>
          <input id="ap-title" type="text" placeholder="DHA Phase 6 — 10 Marla Modern House" required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Society / Area *</label>
            <input id="ap-area" type="text" placeholder="DHA Phase 6" required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Full Location *</label>
            <input id="ap-location" type="text" placeholder="DHA Phase 6, Lahore" required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Property Type *</label>
            <select id="ap-type" required class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 bg-white transition-all">
              <option value="">Select type...</option>
              <option>House</option><option>Bungalow</option><option>Apartment</option>
              <option>Plot</option><option>Commercial Plot</option><option>Shop</option><option>Office</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Area (Marla) *</label>
            <input id="ap-marla" type="number" placeholder="10" step="0.5" min="1" required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Bedrooms</label>
            <input id="ap-beds" type="number" placeholder="0" min="0"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Bathrooms</label>
            <input id="ap-baths" type="number" placeholder="0" min="0"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Price (PKR) *</label>
            <input id="ap-price" type="number" placeholder="45000000" oninput="updateApPriceDisplay()" required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Price Display</label>
            <input id="ap-price-display" readonly placeholder="Auto-calculated"
              class="w-full px-4 py-3 rounded-xl border border-gray-100 bg-gray-50 text-sm font-bold text-emerald-700"/>
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Features (comma separated)</label>
          <input id="ap-features" type="text" placeholder="Corner plot, Near park, Gas available, New construction"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-600 mb-1.5 uppercase tracking-wide">Description</label>
          <textarea id="ap-desc" rows="3" placeholder="Describe the property..."
            class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all resize-none"></textarea>
        </div>
        <!-- Seller info (auto-filled if logged in) -->
        <div id="ap-seller-section" class="p-4 bg-gray-50 rounded-2xl space-y-3 border border-dashed border-gray-200">
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wide">Your Contact Info</p>
          <div class="grid grid-cols-2 gap-3">
            <input id="ap-seller-name" type="text" placeholder="Your Name *"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
            <input id="ap-seller-phone" type="tel" placeholder="Phone Number *"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm font-medium focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"/>
          </div>
        </div>
        <button type="submit"
          class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-sm transition-all active:scale-95 flex items-center justify-center gap-2">
          <span>🚀</span> List Property
        </button>
      </form>
    </div>
  </div>
  `;
  const div = document.createElement('div');
  div.innerHTML = html;
  document.body.appendChild(div);
}

// ── Auth Modal controls ───────────────────────────────────────────────────────
function openAuthModal(defaultTab = 'login') {
  document.getElementById('auth-modal').classList.remove('hidden');
  switchAuthTab(defaultTab);
}
function closeAuthModal() {
  document.getElementById('auth-modal').classList.add('hidden');
}
function switchAuthTab(tab) {
  document.getElementById('auth-login').classList.toggle('hidden', tab !== 'login');
  document.getElementById('auth-signup').classList.toggle('hidden', tab !== 'signup');
  document.getElementById('tab-login').className = `flex-1 py-4 text-sm font-bold tracking-wide border-b-2 transition-all ${tab === 'login' ? 'border-emerald-600 text-emerald-700' : 'border-transparent text-gray-400'}`;
  document.getElementById('tab-signup').className = `flex-1 py-4 text-sm font-bold tracking-wide border-b-2 transition-all ${tab === 'signup' ? 'border-emerald-600 text-emerald-700' : 'border-transparent text-gray-400'}`;
}

function doLogin() {
  const phone = document.getElementById('li-phone').value.trim();
  const name  = document.getElementById('li-name').value.trim();
  if (!phone || !name) { showToast('Please enter your name and phone', 'error'); return; }
  Auth.set({ name, phone, email: '', role: 'buyer' });
  closeAuthModal();
  showToast(`Welcome back, ${name}! 👋`);
  updateNavAuth();
  if (typeof onAuthSuccess === 'function') onAuthSuccess();
}

function doSignup() {
  const fname = document.getElementById('su-fname').value.trim();
  const lname = document.getElementById('su-lname').value.trim();
  const phone = document.getElementById('su-phone').value.trim();
  const email = document.getElementById('su-email').value.trim();
  const role  = document.querySelector('input[name="su-role"]:checked')?.value || 'buyer';
  if (!fname || !phone) { showToast('Name and phone are required', 'error'); return; }
  const name = lname ? `${fname} ${lname}` : fname;
  Auth.set({ name, phone, email, role });
  closeAuthModal();
  showToast(`Account created! Welcome, ${fname}! 🎉`);
  updateNavAuth();
  if (role === 'seller') {
    setTimeout(() => { window.location.href = 'seller_dashboard.html'; }, 800);
  }
  if (typeof onAuthSuccess === 'function') onAuthSuccess();
}

function doLogout() {
  Auth.clear();
  showToast('Signed out. See you soon!');
  updateNavAuth();
  if (typeof onLogout === 'function') onLogout();
}

// ── Update nav bar to reflect login state ────────────────────────────────────
function updateNavAuth() {
  const user = Auth.get();
  // Find all sign-in / list-property buttons added by pages and update them
  document.querySelectorAll('[data-auth-btn]').forEach(btn => {
    if (user) {
      btn.textContent = user.name.split(' ')[0];
      btn.onclick = doLogout;
      btn.classList.add('text-emerald-700');
    } else {
      btn.textContent = 'Sign In';
      btn.onclick = () => openAuthModal('login');
    }
  });
  document.querySelectorAll('[data-list-btn]').forEach(btn => {
    btn.onclick = () => {
      if (Auth.isLoggedIn()) openAddPropModal();
      else { openAuthModal('login'); }
    };
  });
}

// ── Add Property Modal ────────────────────────────────────────────────────────
function openAddPropModal() {
  const user = Auth.get();
  if (!user) { openAuthModal('login'); return; }
  // Pre-fill seller info if logged in
  document.getElementById('ap-seller-name').value  = user.name;
  document.getElementById('ap-seller-phone').value = user.phone;
  document.getElementById('add-prop-modal').classList.remove('hidden');
}
function closeAddPropModal() {
  document.getElementById('add-prop-modal').classList.add('hidden');
  document.getElementById('global-add-form').reset();
  document.getElementById('ap-price-display').value = '';
}
function updateApPriceDisplay() {
  document.getElementById('ap-price-display').value = fmtPrice(document.getElementById('ap-price').value);
}

async function submitAddProperty(e) {
  e.preventDefault();
  const btn = e.submitter || e.target.querySelector('button[type=submit]');
  btn.disabled = true;
  btn.textContent = 'Listing...';
  const body = {
    seller_name:    document.getElementById('ap-seller-name').value.trim(),
    seller_phone:   document.getElementById('ap-seller-phone').value.trim(),
    title:          document.getElementById('ap-title').value,
    area:           document.getElementById('ap-area').value,
    location:       document.getElementById('ap-location').value,
    type:           document.getElementById('ap-type').value,
    area_marla:     parseFloat(document.getElementById('ap-marla').value),
    bedrooms:       parseInt(document.getElementById('ap-beds').value) || 0,
    bathrooms:      parseInt(document.getElementById('ap-baths').value) || 0,
    price_pkr:      parseFloat(document.getElementById('ap-price').value),
    price_display:  document.getElementById('ap-price-display').value,
    features:       document.getElementById('ap-features').value.split(',').map(s => s.trim()).filter(Boolean),
    description:    document.getElementById('ap-desc').value,
  };
  if (!body.seller_name || !body.seller_phone) {
    showToast('Your name and phone are required', 'error');
    btn.disabled = false; btn.innerHTML = '<span>🚀</span> List Property'; return;
  }
  try {
    const r = await fetch(`${API}/api/properties`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const d = await r.json();
    if (d.success) {
      showToast('Property listed successfully! 🎉');
      closeAddPropModal();
      if (typeof onPropertyAdded === 'function') onPropertyAdded(d.property);
    } else {
      showToast(d.detail || 'Failed to list property', 'error');
    }
  } catch {
    showToast('Cannot connect to backend. Is the server running?', 'error');
  }
  btn.disabled = false;
  btn.innerHTML = '<span>🚀</span> List Property';
}

// ── Bootstrap on DOMContentLoaded ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  injectModals();
  updateNavAuth();

  // Close modals on backdrop click
  document.getElementById('auth-modal').addEventListener('click', e => {
    if (e.target === document.getElementById('auth-modal')) closeAuthModal();
  });
  document.getElementById('add-prop-modal').addEventListener('click', e => {
    if (e.target === document.getElementById('add-prop-modal')) closeAddPropModal();
  });
});

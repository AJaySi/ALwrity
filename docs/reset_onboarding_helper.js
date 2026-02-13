// Frontend Onboarding Reset Helper
// Run this in browser console (F12 → Console) to reset onboarding state

console.log('🔄 Starting onboarding reset...');

// Clear localStorage
localStorage.removeItem('onboarding_active_step');
localStorage.removeItem('onboarding_data');
localStorage.removeItem('onboarding_step_data');

// Clear sessionStorage
sessionStorage.removeItem('onboarding_init');

// Clear any other onboarding-related data
Object.keys(localStorage).forEach(key => {
  if (key.includes('onboarding')) {
    localStorage.removeItem(key);
    console.log('🗑️ Cleared localStorage:', key);
  }
});

Object.keys(sessionStorage).forEach(key => {
  if (key.includes('onboarding')) {
    sessionStorage.removeItem(key);
    console.log('🗑️ Cleared sessionStorage:', key);
  }
});

// Reset any React state (if accessible)
if (window.location) {
  console.log('🔄 Reloading page to reset React state...');
  window.location.reload();
}

console.log('✅ Frontend onboarding reset complete!');
console.log('📝 Next: Call the backend reset endpoint or restart the app');
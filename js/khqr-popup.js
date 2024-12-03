'use strict';

// Dependencies: jQuery, Magnific Popup

// Define CurrencyMode as an Enum
const CurrencyMode = {
    A: { key: 'a', imageSrc: 'images/qrcode/khr.webp', altText: 'Khmer Riel' },
    B: { key: 'b', imageSrc: 'images/qrcode/usd.webp', altText: 'US Dollar' }
};

// Helper function to get currency mode by key
function getCurrencyMode(key) {
    return Object.values(CurrencyMode).find(mode => mode.key === key);
}

// Popup Management Variables
let popupTimeout = null; // Stores the timeout ID for the popup
let activeKey = null; // Tracks the currently active key

// Function to show/hide popups
function handlePopup(mode) {
    // Reset the timer if the same key is pressed
    clearTimeout(popupTimeout);

    if (activeKey !== mode.key) {
        // Show the popup
        $.magnificPopup.open({
            items: {
                src: `<div class="white-popup"><img src="${mode.imageSrc}" alt="${mode.altText}"></div>`,
                type: 'inline'
            }
        });
        activeKey = mode.key; // Set the active key
    }

    // Set or reset the timer to close the popup after 3 seconds
    popupTimeout = setTimeout(() => {
        $.magnificPopup.close();
        activeKey = null; // Reset the active key
    }, 3000); // 3000 ms = 3 seconds
}
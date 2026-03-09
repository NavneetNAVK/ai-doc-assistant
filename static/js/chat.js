/*
====================================================================
 FILE: chat.js
 PURPOSE: Client-side behavior for AI Workspace chat UI
 STATUS: PRODUCTION – DO NOT MODIFY WITHOUT REVIEW
 DEPENDENCIES:
  - chat.html
  - sidebar.html
  - chat_window.html
  - pdf_modal.html
====================================================================
*/

/*
    ====================================================================
     AUTO-SCROLL LOGIC
     ------------------------------------------------------------------
     Keeps the chat window scrolled to the bottom whenever:
     - Page loads
     - New messages are added to the DOM
    ====================================================================
    */

    // Reference to chat window container
    const chatWindow = document.getElementById('chat-window');

    // Scroll helper
    if(chatWindow) {
        function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    }
    

    // Scroll on initial load
    window.onload = scrollToBottom;

    // Observe DOM changes inside chat window
    const observer = new MutationObserver(scrollToBottom);

    observer.observe(chatWindow, {
        childList: true
    });



    /*
    ====================================================================
     PDF VIEWER LOGIC
     ------------------------------------------------------------------
     Handles:
     - Opening PDF preview modal
     - Closing modal
     - Resetting iframe source
    ====================================================================
    */

    // Modal elements
    const modal = document.getElementById('pdfModal');
    const frame = document.getElementById('pdfFrame');

    // Open PDF modal
    function openPDFViewer(url) {
        frame.src = url;
        modal.style.display = 'flex';
    }

    // Close PDF modal
    function closePDFViewer() {
        modal.style.display = 'none';
        frame.src = '';
    }

    // Close modal when clicking outside content
    window.onclick = function(event) {
        if (event.target === modal) {
            closePDFViewer();
        }
    };



    /*
    ====================================================================
     SIDEBAR TOGGLE LOGIC
     ------------------------------------------------------------------
     Controls collapsing / expanding the sidebar.

     NOTE:
     - Applies to BOTH menu buttons:
       1. Sidebar hamburger
       2. Top-bar backup menu
    ====================================================================
    */

    // Sidebar element
    const sidebar = document.querySelector('.sidebar');

    // Select all menu buttons
    const menuBtns = document.querySelectorAll('.menu-btn');

    // Toggle sidebar on click
    if (sidebar && menuBtns.length) {

        menuBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    });
    }
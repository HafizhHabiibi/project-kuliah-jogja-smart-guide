/**
 * Jogja Smart Guide — Admin Dashboard JS
 * Photo preview, delete confirmation, table search, sidebar toggle
 */

document.addEventListener('DOMContentLoaded', () => {
    initPhotoPreview();
    initTableSearch();
    initSidebarToggle();
    initFlashAutoClose();
});


/**
 * Photo upload preview
 */
function initPhotoPreview() {
    const fileInput = document.getElementById('photo');
    const previewArea = document.getElementById('photo-preview');
    const uploadArea = document.getElementById('photo-upload-area');

    if (!fileInput || !previewArea) return;

    // Click on preview area triggers file input
    previewArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    if (uploadArea) {
        ['dragenter', 'dragover'].forEach(evt => {
            uploadArea.addEventListener(evt, (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
        });
        ['dragleave', 'drop'].forEach(evt => {
            uploadArea.addEventListener(evt, (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
            });
        });
        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                showPreview(files[0]);
            }
        });
    }

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            showPreview(e.target.files[0]);
        }
    });

    function showPreview(file) {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            // Clear existing elements in preview area safely
            while (previewArea.firstChild) {
                previewArea.removeChild(previewArea.firstChild);
            }

            // Create image element
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = 'Preview';
            img.id = 'preview-img';

            // Create instructions span
            const span = document.createElement('span');
            span.className = 'admin-photo-change';
            span.textContent = 'Klik untuk ganti foto';

            // Append new preview elements
            previewArea.appendChild(img);
            previewArea.appendChild(span);
        };
        reader.readAsDataURL(file);
    }
}


/**
 * Delete confirmation modal
 */
function confirmDelete(destId, destName) {
    const modal = document.getElementById('delete-modal');
    const nameEl = document.getElementById('delete-dest-name');
    const form = document.getElementById('delete-form');

    if (modal && nameEl && form) {
        nameEl.textContent = destName;
        form.action = `/admin/destination/delete/${destId}`;
        modal.style.display = 'flex';
        // Animate in
        requestAnimationFrame(() => modal.classList.add('show'));
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => { modal.style.display = 'none'; }, 200);
    }
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'delete-modal') {
        closeDeleteModal();
    }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDeleteModal();
});


/**
 * Table search functionality
 */
function initTableSearch() {
    const searchInput = document.getElementById('admin-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase().trim();
        const rows = document.querySelectorAll('.admin-table-row');

        rows.forEach(row => {
            const name = row.getAttribute('data-name') || '';
            row.style.display = name.includes(query) ? '' : 'none';
        });
    });
}


/**
 * Sidebar toggle (mobile)
 */
function initSidebarToggle() {
    const toggle = document.getElementById('admin-menu-toggle');
    const sidebar = document.getElementById('admin-sidebar');

    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 &&
            sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}


/**
 * Auto-close flash messages
 */
function initFlashAutoClose() {
    const messages = document.querySelectorAll('.flash-message');
    messages.forEach((msg, i) => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        }, 4000 + i * 500);
    });
}

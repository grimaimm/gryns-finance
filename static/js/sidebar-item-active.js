document.addEventListener('DOMContentLoaded', function () {
  // Fungsi untuk menangani klik tautan navbar dan memperbarui status aktif
  function changeTab(tabId) {
      const navbarLinks = document.querySelectorAll('.sidebar-nav .sidebar-item');

      navbarLinks.forEach(link => {
          link.classList.remove('active');
      });

      const activeLink = document.querySelector(`.sidebar-nav .sidebar-item[href="#${tabId}"]`);
      activeLink.classList.add('active');
  }
});
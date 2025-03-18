class UIManager {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.menuButtons = document.querySelectorAll('.menu-btn');
        this.settingsBtn = document.querySelector('.settings-btn');
        this.dropdownContent = document.querySelector('.dropdown-content');
        
        this.initializeEventListeners();
        this.setActiveButton();
    }

    initializeEventListeners() {
        // Menu button clicks
        this.menuButtons.forEach(button => {
            button.addEventListener('click', () => this.handleMenuClick(button));
        });

        // Settings dropdown
        this.settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });

        document.addEventListener('click', () => this.hideDropdown());
    }

    handleMenuClick(button) {
        const targetPage = button.dataset.page;
        this.updateActiveButton(button);
        this.navigateToPage(targetPage);
    }

    updateActiveButton(activeButton) {
        this.menuButtons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    }

    setActiveButton() {
        const currentPath = window.location.pathname.substring(1) || 'home';
        this.menuButtons.forEach(button => {
            if (button.dataset.page === currentPath) {
                button.classList.add('active');
            }
        });
    }

    navigateToPage(page) {
        if (page === 'home') {
            window.location.href = '/';
        } else {
            window.location.href = `/${page}`;
        }
    }

    toggleDropdown() {
        this.dropdownContent.style.display = 
            this.dropdownContent.style.display === 'block' ? 'none' : 'block';
    }

    hideDropdown() {
        this.dropdownContent.style.display = 'none';
    }
}

class TabManager {
    constructor() {
        if (!this.isHomePage()) return;

        this.gridItems = document.querySelectorAll('.grid-item');
        this.tabInfo = document.querySelector('.tab-info');
        this.searchInput = document.querySelector('.search-box input');
        this.tabItems = document.querySelectorAll('.tab-item');
        
        this.initializeEventListeners();
        this.initializeFirstTab();
    }

    isHomePage() {
        return window.location.pathname === '/' || window.location.pathname === '/home';
    }

    initializeEventListeners() {
        // Tab clicks
        this.tabItems.forEach(tab => {
            tab.addEventListener('click', () => this.handleTabClick(tab));
        });

        // Search
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
    }

    handleTabClick(tab) {
        const tabName = tab.querySelector('.tab-name').textContent;
        const isActive = tab.querySelector('.tab-status').classList.contains('active');
        
        this.updateTabContent(tabName, isActive);
        this.updateActiveTab(tab);
    }

    updateTabContent(name, status) {
        // Update grid items
        this.gridItems.forEach((item, index) => {
            item.innerHTML = status ? `<h4>${name} - Box ${index + 1}</h4>` : '';
        });

        // Update tab info
        this.tabInfo.innerHTML = status ? `
            <h3>${name}</h3>
            <p>Trạng thái: Hoạt động</p>
            <p>Cập nhật lần cuối: ${new Date().toLocaleString()}</p>
            <div class="tab-details">
                <p>Thông tin chi tiết về ${name}</p>
                <ul>
                    <li>Thông số 1: Giá trị 1</li>
                    <li>Thông số 2: Giá trị 2</li>
                    <li>Thông số 3: Giá trị 3</li>
                </ul>
            </div>
        ` : `
            <h3>${name}</h3>
            <p>Trạng thái: Không hoạt động</p>
            <p>Tab hiện không có dữ liệu</p>
        `;
    }

    updateActiveTab(activeTab) {
        this.tabItems.forEach(item => item.classList.remove('selected'));
        activeTab.classList.add('selected');
    }

    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        this.tabItems.forEach(tab => {
            const tabName = tab.querySelector('.tab-name').textContent.toLowerCase();
            tab.style.display = tabName.includes(searchTerm) ? 'flex' : 'none';
        });
    }

    initializeFirstTab() {
        if (this.tabItems.length > 0) {
            const firstTab = this.tabItems[0];
            const tabName = firstTab.querySelector('.tab-name').textContent;
            const isActive = firstTab.querySelector('.tab-status').classList.contains('active');
            
            this.updateTabContent(tabName, isActive);
            this.updateActiveTab(firstTab);
        }
    }
}

// Initialize managers when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new UIManager();
    new TabManager();
}); 
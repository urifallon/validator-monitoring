// Định nghĩa hàm showPage trước khi sử dụng
function showPage(page) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => p.style.display = 'none');
    
    const currentPage = document.querySelector(`.${page}-page`);
    if (currentPage) {
        currentPage.style.display = 'block';
        
        // Khởi tạo manager tương ứng
        if (page === 'dashboard') {
            new DashboardManager();
        } else if (page === 'manage') {
            new ManageManager();
        }
    }
}

class UIManager {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.menuButtons = document.querySelectorAll('.menu-btn');
        this.settingsBtn = document.querySelector('.settings-btn');
        this.dropdownContent = document.querySelector('.dropdown-content');
        this.menuToggle = document.querySelector('.menu-toggle');
        this.overlay = document.querySelector('.menu-overlay');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Menu toggle functionality
        if (this.menuToggle && this.sidebar && this.overlay) {
            this.menuToggle.addEventListener('click', () => {
                this.sidebar.classList.toggle('collapsed');
                this.overlay.classList.toggle('active');
            });
            
            this.overlay.addEventListener('click', () => {
                this.sidebar.classList.remove('collapsed');
                this.overlay.classList.remove('active');
            });
        }
        
        // Menu button clicks
        this.menuButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleMenuClick(button);
            });
        });

        // Settings dropdown
        if (this.settingsBtn) {
            this.settingsBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
            
            document.addEventListener('click', () => this.hideDropdown());
        }
    }

    handleMenuClick(button) {
        const targetPage = button.dataset.page;
        
        // Nếu đang ở cùng một trang, không làm gì cả
        if (button.classList.contains('active')) {
            return;
        }
        
        this.updateActiveButton(button);
        
        // Sử dụng showPage để chuyển trang SPA-style
        showPage(targetPage);
        
        // Cập nhật URL nhưng không reload trang
        window.history.pushState({page: targetPage}, targetPage, targetPage === 'dashboard' ? '/' : `/${targetPage}`);
    }

    updateActiveButton(activeButton) {
        this.menuButtons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    }

    toggleDropdown() {
        if (this.dropdownContent) {
            this.dropdownContent.style.display = 
                this.dropdownContent.style.display === 'block' ? 'none' : 'block';
        }
    }

    hideDropdown() {
        if (this.dropdownContent) {
            this.dropdownContent.style.display = 'none';
        }
    }
}

class DashboardManager {
    constructor() {
        if (!this.isDashboardPage()) return;

        this.gridItems = document.querySelectorAll('.grid-item');
        this.tabInfo = document.querySelector('.tab-info');
        this.searchInput = document.querySelector('.search-box input');
        this.vpsList = document.getElementById('vps-list');
        
        this.initializeEventListeners();
        this.loadVPSList();
        this.setupVPSSearch();
        this.startStatusCheck();
    }

    isDashboardPage() {
        return window.location.pathname === '/' || window.location.pathname === '/dashboard';
    }

    initializeEventListeners() {
        // Search
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
    }

    async loadVPSList() {
        try {
            const response = await fetch('/api/vps');
            const vpsList = await response.json();
            
            this.vpsList.innerHTML = '';
            
            vpsList.forEach(vps => {
                const vpsElement = this.createVPSElement(vps);
                this.vpsList.appendChild(vpsElement);
            });

            // Select first VPS if available
            if (vpsList.length > 0) {
                this.selectVPS(vpsList[0]);
            }
        } catch (error) {
            console.error('Error loading VPS list:', error);
        }
    }

    createVPSElement(vps) {
        const div = document.createElement('div');
        div.className = 'tab-item';
        div.dataset.vpsId = vps.id;
        
        div.innerHTML = `
            <span class="tab-name">${vps.name}</span>
            <span class="tab-status ${vps.status ? 'active' : 'inactive'}">${vps.status ? 'ON' : 'OFF'}</span>
        `;
        
        div.addEventListener('click', () => this.selectVPS(vps));
        return div;
    }

    async selectVPS(vps) {
        try {
            // Update Grafana panels
            this.updateGrafanaPanels(vps);
            
            // Update active state in VPS list
            const vpsItems = document.querySelectorAll('.tab-item');
            vpsItems.forEach(item => item.classList.remove('active'));
            document.querySelector(`[data-vps-id="${vps.id}"]`).classList.add('active');
        } catch (error) {
            console.error('Error selecting VPS:', error);
        }
    }

    updateGrafanaPanels(vps) {
        // Kiểm tra xem có dashboard ID không
        if (!vps.grafana_dashboard_id) {
            console.log('Không có Grafana dashboard ID cho VPS này');
            
            // Hiển thị thông báo trong các panel
            const panels = {
                'cpu-panel': 'Không có dữ liệu CPU',
                'ram-panel': 'Không có dữ liệu RAM',
                'network-panel': 'Không có dữ liệu Network',
                'disk-panel': 'Không có dữ liệu Disk',
                'gpu-panel': 'Không có dữ liệu GPU',
                'logs-panel': 'Không có dữ liệu Logs'
            };
            
            Object.entries(panels).forEach(([id, message]) => {
                const panel = document.getElementById(id);
                if (panel) {
                    // Nếu là iframe, thay bằng div chứa thông báo
                    const parent = panel.parentElement;
                    const tempDiv = document.createElement('div');
                    tempDiv.id = id;
                    tempDiv.className = 'no-data-panel';
                    tempDiv.innerHTML = `<p>${message}</p><p>VPS: ${vps.name}</p>`;
                    parent.replaceChild(tempDiv, panel);
                }
            });
            return;
        }
        
        // Nếu có dashboard ID, hiển thị iframe Grafana
        // Sử dụng URL cố định cho demo, trong thực tế nên lấy từ server
        const grafanaUrl = 'http://your-grafana-url:3000';
        const panels = {
            'cpu-panel': `${grafanaUrl}/d/${vps.grafana_dashboard_id}?panelId=1&orgId=1&theme=light`,
            'ram-panel': `${grafanaUrl}/d/${vps.grafana_dashboard_id}?panelId=2&orgId=1&theme=light`,
            'network-panel': `${grafanaUrl}/d/${vps.grafana_dashboard_id}?panelId=3&orgId=1&theme=light`,
            'disk-panel': `${grafanaUrl}/d/${vps.grafana_dashboard_id}?panelId=4&orgId=1&theme=light`,
            'gpu-panel': `${grafanaUrl}/d/${vps.grafana_dashboard_id}?panelId=5&orgId=1&theme=light`,
            'logs-panel': `${grafanaUrl}/d/${vps.grafana_dashboard_id}?panelId=6&orgId=1&theme=light`
        };
        
        Object.entries(panels).forEach(([id, url]) => {
            const panel = document.getElementById(id);
            if (panel) {
                // Nếu không phải iframe, tạo iframe mới
                if (panel.tagName !== 'IFRAME') {
                    const parent = panel.parentElement;
                    const iframe = document.createElement('iframe');
                    iframe.id = id;
                    iframe.src = url;
                    iframe.frameBorder = '0';
                    iframe.allowFullscreen = true;
                    parent.replaceChild(iframe, panel);
                } else {
                    // Nếu đã là iframe, cập nhật src
                    panel.src = url;
                }
            }
        });
    }

    async checkVPSStatuses() {
        const vpsItems = document.querySelectorAll('.tab-item');
        for (const item of vpsItems) {
            const vpsId = item.dataset.vpsId;
            try {
                const response = await fetch(`/api/vps/${vpsId}/status`);
                const data = await response.json();
                
                const statusSpan = item.querySelector('.tab-status');
                statusSpan.className = `tab-status ${data.status ? 'active' : 'inactive'}`;
                statusSpan.textContent = data.status ? 'ON' : 'OFF';
            } catch (error) {
                console.error(`Error checking status for VPS ${vpsId}:`, error);
            }
        }
    }

    startStatusCheck() {
        setInterval(() => this.checkVPSStatuses(), 30000); // Check every 30 seconds
    }

    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const vpsItems = document.querySelectorAll('.tab-item');
        
        vpsItems.forEach(item => {
            const vpsName = item.querySelector('.tab-name').textContent.toLowerCase();
            item.style.display = vpsName.includes(searchTerm) ? 'flex' : 'none';
        });
    }

    setupVPSSearch() {
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
    }
}

class ManageManager {
    constructor() {
        if (!this.isManagePage()) return;
        this.initializeEventListeners();
    }

    isManagePage() {
        return window.location.pathname === '/manage';
    }

    initializeEventListeners() {
        const addVPSForm = document.getElementById('addVPSForm');
        if (addVPSForm) {
            addVPSForm.addEventListener('submit', (e) => this.handleAddVPS(e));
        }
    }

    async handleAddVPS(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('vpsName').value,
            ip_address: document.getElementById('vpsIP').value,
            type: document.getElementById('vpsType').value,
            port: parseInt(document.getElementById('vpsPort').value)
        };

        // Validation
        if (!formData.name || !formData.ip_address || !formData.type || !formData.port) {
            alert('Vui lòng điền đầy đủ thông tin');
            return;
        }

        try {
            // Thêm loading state
            const submitBtn = document.querySelector('.submit-btn');
            submitBtn.textContent = 'Đang xử lý...';
            submitBtn.disabled = true;

            const response = await fetch('/api/vps', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            // Reset button
            submitBtn.textContent = 'Thêm VPS';
            submitBtn.disabled = false;

            if (response.ok) {
                const result = await response.json();
                alert('Thêm VPS thành công!');
                this.resetForm();
                
                // Chuyển đến trang dashboard và cập nhật danh sách VPS
                const dashboardButton = document.querySelector('.menu-btn[data-page="dashboard"]');
                if (dashboardButton) {
                    // Mô phỏng sự kiện click vào nút dashboard
                    dashboardButton.click();
                } else {
                    // Nếu không tìm thấy nút, chuyển trang trực tiếp
                    showPage('dashboard');
                    const dashboardManager = new DashboardManager();
                }
            } else {
                const error = await response.json();
                alert('Lỗi: ' + (error.message || 'Không thể thêm VPS'));
            }
        } catch (error) {
            console.error('Error adding VPS:', error);
            alert('Có lỗi xảy ra khi thêm VPS');
            
            // Reset button
            const submitBtn = document.querySelector('.submit-btn');
            submitBtn.textContent = 'Thêm VPS';
            submitBtn.disabled = false;
        }
    }

    resetForm() {
        document.getElementById('addVPSForm').reset();
    }
}

// Initialize managers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Tạo một instance của UI Manager để xử lý sự kiện sidebar và menu
    const uiManager = new UIManager();
    
    // Xác định trang hiện tại dựa vào URL
    const path = window.location.pathname;
    let currentPage = 'dashboard'; // Mặc định
    
    if (path === '/' || path === '/dashboard') {
        currentPage = 'dashboard';
    } else if (path === '/manage') {
        currentPage = 'manage';
    } else if (path === '/stats') {
        currentPage = 'stats';
    } else if (path === '/settings') {
        currentPage = 'settings';
    } else if (path === '/info') {
        currentPage = 'info';
    }
    
    // Hiển thị trang hiện tại và khởi tạo manager tương ứng
    showPage(currentPage);
    
    // Đánh dấu nút menu tương ứng
    const activeButton = document.querySelector(`.menu-btn[data-page="${currentPage}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    // Xử lý sự kiện popstate khi người dùng nhấn nút back/forward của trình duyệt
    window.addEventListener('popstate', function(event) {
        const path = window.location.pathname;
        let currentPage = 'dashboard';
        
        if (path === '/' || path === '/dashboard') {
            currentPage = 'dashboard';
        } else if (path === '/manage') {
            currentPage = 'manage';
        } else if (path === '/stats') {
            currentPage = 'stats';
        } else if (path === '/settings') {
            currentPage = 'settings';
        } else if (path === '/info') {
            currentPage = 'info';
        }
        
        // Hiển thị trang tương ứng
        showPage(currentPage);
        
        // Cập nhật nút menu active
        const menuButtons = document.querySelectorAll('.menu-btn');
        menuButtons.forEach(btn => btn.classList.remove('active'));
        const activeButton = document.querySelector(`.menu-btn[data-page="${currentPage}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    });
}); 
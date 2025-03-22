import requests
from datetime import datetime

def check_vps_status(vps):
    """
    Kiểm tra trạng thái của VPS bằng cách ping đến cổng node_exporter
    
    Args:
        vps: Đối tượng VPS cần kiểm tra
        
    Returns:
        bool: True nếu VPS hoạt động, False nếu ngược lại
    """
    try:
        # Thử kết nối với node_exporter
        response = requests.get(
            f"http://{vps.ip_address}:{vps.port_exporter}/metrics", 
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error checking VPS status: {e}")
        return False
        
def get_vps_metrics(vps):
    """
    Lấy metrics từ node_exporter
    
    Args:
        vps: Đối tượng VPS cần lấy metrics
        
    Returns:
        dict: Các metrics của VPS
    """
    try:
        response = requests.get(
            f"http://{vps.ip_address}:{vps.port_exporter}/metrics", 
            timeout=5
        )
        
        if response.status_code == 200:
            # TODO: Parse metrics from node_exporter response
            # Cho phiên bản demo, chúng ta trả về một số metrics giả lập
            return {
                'cpu_usage': 25.5,
                'memory_usage': 40.2,
                'disk_usage': 60.8,
                'network_rx': 1024,
                'network_tx': 2048
            }
        return None
    except Exception as e:
        print(f"Error getting VPS metrics: {e}")
        return None
        
def check_promtail_status(vps):
    """
    Kiểm tra trạng thái của Promtail trên VPS
    
    Args:
        vps: Đối tượng VPS cần kiểm tra
        
    Returns:
        bool: True nếu Promtail hoạt động, False nếu ngược lại
    """
    try:
        # Thử kết nối với Promtail API
        response = requests.get(
            f"http://{vps.ip_address}:{vps.port_promtail}/ready", 
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error checking Promtail status: {e}")
        return False 
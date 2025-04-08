from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
import urllib.parse

# 初始化浏览器（修复缺失的driver初始化）
def init_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        
        # 添加 Chrome 安装路径（根据实际路径修改）
        options.binary_location = os.getenv('CHROME_BIN', r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        
        # 手动指定 ChromeDriver 版本
        driver_path = os.getenv('CHROMEDRIVER_PATH', ChromeDriverManager(version="124.0.6367.91").install())
        
        driver = webdriver.Chrome(
            service=Service(executable_path=driver_path),
            options=options
        )
        return driver
    except Exception as e:
        print(f"初始化失败细节: {str(e)}")
        # 尝试备用方法
        try:
            return webdriver.Chrome(options=options)
        except:
            print("请手动下载ChromeDriver：https://registry.npmmirror.com/binary.html?path=chromedriver/")
            exit(1)

# 创建保存目录
save_dir = "Cache/CardStorage"
os.makedirs(save_dir, exist_ok=True)

# 主程序
def main():
    driver = init_driver()
    
    try:
        driver.get("https://hs.blizzard.cn/cards/")
        print("页面加载完成，开始滚动...")

        # 优化滚动加载逻辑
        last_count = 0
        retry = 0
        while retry < 5:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 获取当前图片数量
            current_imgs = driver.find_elements(By.CSS_SELECTOR, ".card_list_box img")
            if len(current_imgs) == last_count:
                retry += 1
            else:
                last_count = len(current_imgs)
                retry = 0
            print(f"已加载 {len(current_imgs)} 张卡牌")

        # 提取图片信息
        img_elements = driver.find_elements(By.CSS_SELECTOR, ".card_list_box img")
        print(f"共发现 {len(img_elements)} 张卡牌")

        # 下载图片
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        for idx, img in enumerate(img_elements):
            try:
                url = img.get_attribute("src")
                alt_name = urllib.parse.unquote(img.get_attribute("alt").strip() or f"card_{idx}")
                
                # 清理非法文件名字符
                safe_name = "".join([c for c in alt_name if c not in r'\/:*?"<>|']).strip()
                file_path = os.path.join(save_dir, f"{safe_name}.png")

                if os.path.exists(file_path):
                    print(f"已存在: {safe_name}")
                    continue

                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"下载成功：{safe_name}")
                else:
                    print(f"下载失败[{response.status_code}]：{safe_name}")

            except Exception as e:
                print(f"错误 {type(e).__name__}：{str(e)}")
            finally:
                time.sleep(0.3)

    finally:
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"总耗时：{time.time()-start_time:.2f}秒")
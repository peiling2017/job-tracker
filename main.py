import time
import random
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

from config import *

class ConservativeLinkedInScraper:
    def __init__(self):
        self.driver = None
        self.jobs_data = []
        self.session_start_time = None
        
    def setup_driver(self):
        """安全设置浏览器驱动"""
        print("🚀 启动浏览器（安全模式）...")
        chrome_options = Options()
        
        # 反检测设置
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(BROWSER_CONFIG["implicit_wait"])
        print("✅ 浏览器启动成功 - 安全模式激活")
        
    def safe_delay(self, min_seconds=None, max_seconds=None):
        """安全延迟"""
        if min_seconds is None:
            min_seconds = SAFETY_CONFIG["delay_between_jobs"][0]
        if max_seconds is None:
            max_seconds = SAFETY_CONFIG["delay_between_jobs"][1]
            
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def simulate_human_behavior(self):
        """模拟人类行为"""
        # 随机鼠标移动
        if random.random() > 0.7:
            try:
                actions = ActionChains(self.driver)
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset).perform()
                actions.move_by_offset(-x_offset, -y_offset).perform()
            except:
                pass
        
        # 随机滚动
        if random.random() > 0.5:
            try:
                scroll_pixels = random.randint(200, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            except:
                pass
        
        self.safe_delay(1, 3)
    
    def build_search_url(self):
        """构建搜索URL"""
        base_url = LINKEDIN_URL
        params = []
        
        for key, value in SEARCH_PARAMS.items():
            params.append(f"{key}={value}")
        
        search_url = f"{base_url}?{'&'.join(params)}"
        print(f"🔍 搜索目标: 德国五大城市 | 现场/混合办公 | 24小时内发布")
        return search_url
    
    def detect_english(self, text):
        """检测英文职位描述"""
        if not text:
            return 0.0
            
        text_lower = text.lower()
        matches = 0
        total_keywords = len(ENGLISH_DETECTION["required_keywords"])
        
        for keyword in ENGLISH_DETECTION["required_keywords"]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                matches += 1
        
        return matches / total_keywords
    
    def extract_work_arrangement(self, description, location_text):
        """提取工作安排类型"""
        text = (description + " " + location_text).lower()
        
        if "hybrid" in text:
            return "hybrid"
        elif "on-site" in text or "on site" in text or "office" in text:
            return "on-site"
        elif "remote" in text or "work from home" in text:
            return "remote"
        else:
            return "unknown"
    
    def check_safety_limits(self, current_count):
        """检查安全限制"""
        if current_count >= SAFETY_CONFIG["max_jobs_per_session"]:
            print(f"🛑 达到会话上限: {SAFETY_CONFIG['max_jobs_per_session']} 个职位")
            return False
        
        # 每处理10个职位休息一次
        if current_count > 0 and current_count % SAFETY_CONFIG["session_break_after"] == 0:
            break_time = random.randint(SAFETY_CONFIG["break_duration"][0], SAFETY_CONFIG["break_duration"][1])
            print(f"⏸️  安全暂停 {break_time} 秒...")
            time.sleep(break_time)
            
        return True
    
    def scrape_jobs(self):
        """安全爬取职位数据"""
        try:
            # 访问搜索页面
            search_url = self.build_search_url()
            self.driver.get(search_url)
            
            print("⏳ 等待页面加载...")
            self.safe_delay(5, 8)
            
            # 等待职位列表
            WebDriverWait(self.driver, 25).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            
            job_count = 0
            processed_count = 0
            
            while self.check_safety_limits(processed_count):
                try:
                    # 获取职位列表
                    job_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, "li.jobs-search-results__list-item"
                    )
                    
                    if job_count >= len(job_elements):
                        print("📭 没有更多职位了")
                        break
                    
                    print(f"\n📋 处理职位 {processed_count + 1}/{SAFETY_CONFIG['max_jobs_per_session']}")
                    
                    # 模拟人类行为
                    self.simulate_human_behavior()
                    
                    # 点击职位
                    job_element = job_elements[job_count]
                    self.driver.execute_script("arguments[0].click();", job_element)
                    self.safe_delay(3, 5)
                    
                    # 提取职位信息
                    job_data = self.extract_job_details()
                    if job_data:
                        # 分析职位
                        english_score = self.detect_english(job_data.get('description', ''))
                        is_english = english_score >= ENGLISH_DETECTION["min_english_score"]
                        
                        job_data['english_score'] = round(english_score, 2)
                        job_data['is_english'] = is_english
                        job_data['work_arrangement'] = self.extract_work_arrangement(
                            job_data.get('description', ''),
                            job_data.get('location', '')
                        )
                        
                        self.jobs_data.append(job_data)
                        
                        status = "✅ 英文" if is_english else "❌ 非英文"
                        work_type = job_data['work_arrangement']
                        print(f"   {job_data['title']}")
                        print(f"   {job_data['company']} | {job_data['location']}")
                        print(f"   📊 英文评分: {english_score:.2f} | 工作类型: {work_type} | {status}")
                        
                        processed_count += 1
                    
                    job_count += 1
                    
                    # 滚动到下一个职位
                    if job_count < len(job_elements):
                        try:
                            next_job = job_elements[job_count]
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_job)
                            self.safe_delay(1, 2)
                        except:
                            pass
                    
                except Exception as e:
                    print(f"⚠️ 处理职位时出错: {e}")
                    job_count += 1
                    self.safe_delay(5, 8)  # 出错时延长延迟
                    continue
            
            print(f"\n🎉 会话完成! 安全处理 {len(self.jobs_data)} 个职位")
            
        except Exception as e:
            print(f"❌ 爬取过程中出错: {e}")
    
    def extract_job_details(self):
        """提取职位详情"""
        try:
            job_data = {}
            
            # 提取标题
            try:
                title_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".job-details-jobs-unified-top-card__job-title, h2.job-details-jobs-unified-top-card__job-title"
                )
                job_data['title'] = title_element.text.strip()
            except:
                job_data['title'] = "Unknown Title"
            
            # 提取公司
            try:
                company_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".job-details-jobs-unified-top-card__company-name a, .job-details-jobs-unified-top-card__company-name"
                )
                job_data['company'] = company_element.text.strip()
            except:
                job_data['company'] = "Unknown Company"
            
            # 提取地点
            try:
                location_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".job-details-jobs-unified-top-card__primary-description-container, .job-details-jobs-unified-top-card__bullet"
                )
                location_text = location_element.text
                if '·' in location_text:
                    parts = location_text.split('·')
                    if len(parts) > 1:
                        job_data['location'] = parts[1].strip()
                    else:
                        job_data['location'] = location_text.strip()
                else:
                    job_data['location'] = location_text.strip()
            except:
                job_data['location'] = "Unknown Location"
            
            # 提取职位描述
            try:
                # 尝试点击"显示更多"
                try:
                    show_more_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "button[aria-label='Show more']"
                    )
                    for button in show_more_buttons:
                        self.driver.execute_script("arguments[0].click();", button)
                        self.safe_delay(1, 2)
                except:
                    pass
                
                description_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "#job-details, .jobs-description, .jobs-description-content"
                )
                job_data['description'] = description_element.text.strip()
            except:
                job_data['description'] = ""
            
            # 提取职位链接
            try:
                job_link_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "a.jobs-search__job-details--container-embedded-link"
                )
                job_data['job_url'] = job_link_element.get_attribute('href')
            except:
                job_data['job_url'] = self.driver.current_url
            
            job_data['scraped_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return job_data
            
        except Exception as e:
            print(f"⚠️ 提取职位详情时出错: {e}")
            return None
    
    def save_to_excel(self):
        """保存结果到Excel"""
        if not self.jobs_data:
            print("❌ 没有数据可保存")
            return
        
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        filename = f"german_jobs_{timestamp}.xlsx"
        
        df = pd.DataFrame(self.jobs_data)
        
        # 重新排列列的顺序
        column_order = [
            'title', 'company', 'location', 'work_arrangement', 
            'is_english', 'english_score', 'job_url', 'scraped_at'
        ]
        
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in column_order]
        
        df = df[existing_columns + other_columns]
        
        # 创建Excel文件
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 所有职位
            df.to_excel(writer, sheet_name='All Jobs', index=False)
            
            # 仅英文职位
            english_jobs = df[df['is_english'] == True]
            english_jobs.to_excel(writer, sheet_name='English Jobs', index=False)
            
            # 按工作类型分类
            for work_type in ['hybrid', 'on-site']:
                type_jobs = english_jobs[english_jobs['work_arrangement'] == work_type]
                if not type_jobs.empty:
                    type_jobs.to_excel(writer, sheet_name=f'{work_type.title()} Jobs', index=False)
        
        print(f"💾 数据已保存到: {filename}")
        print(f"📊 本次会话统计:")
        print(f"   总职位数: {len(df)}")
        print(f"   英文职位: {len(english_jobs)}")
        
        if not english_jobs.empty:
            print("   工作类型分布:")
            work_stats = english_jobs['work_arrangement'].value_counts()
            for work_type, count in work_stats.items():
                print(f"     {work_type}: {count}")
    
    def close(self):
        """安全关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔚 浏览器已安全关闭")

def main():
    print("=" * 50)
    print("🇩🇪 LinkedIn德国职位筛选器 - 保守安全模式")
    print("=" * 50)
    
    scraper = ConservativeLinkedInScraper()
    
    try:
        # 设置浏览器
        scraper.setup_driver()
        
        # 安全提示
        print("\n🔐 安全提示:")
        print("   • 请在浏览器中登录LinkedIn账号")
        print("   • 登录后脚本将自动开始（安全延迟）")
        print("   • 本次会话最多处理20个职位")
        print("   • 推荐每天运行2-3次，间隔4小时")
        input("\n   按回车键继续...")
        
        # 开始爬取
        scraper.scrape_jobs()
        
        # 保存结果
        if scraper.jobs_data:
            scraper.save_to_excel()
            print(f"\n🎯 会话完成!")
            print("   下次运行建议在4小时之后")
        else:
            print("❌ 没有找到职位数据")
            
    except Exception as e:
        print(f"💥 程序运行出错: {e}")
        print("建议检查网络连接或稍后重试")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()

import time
import random
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# 简化配置
SEARCH_CONFIG = {
    "location": "Berlin, Germany",  # 先用柏林测试
    "max_jobs": 10,  # 减少数量测试
    "work_types": ["hybrid", "on-site"]
}

class SimpleLinkedInScraper:
    def __init__(self):
        self.driver = None
        self.jobs_data = []
        
    def setup_driver(self):
        """设置浏览器驱动"""
        print("🚀 启动浏览器...")
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        service = Service()
        
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ 浏览器启动成功！")
            return True
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            return False
    
    def build_search_url(self):
        """构建搜索URL"""
        base_url = "https://www.linkedin.com/jobs/search/"
        params = [
            f"location={SEARCH_CONFIG['location']}",
            "f_TPR=r86400",  # 24小时内
            "f_WT=1,3",      # 现场+混合办公
            "f_JT=F",        # 全职
        ]
        return f"{base_url}?{'&'.join(params)}"
    
    def wait_for_manual_login(self):
        """等待手动登录"""
        print("👤 请在浏览器中手动登录LinkedIn")
        print("   完成登录后回到这里按回车继续...")
        input()
        time.sleep(3)
    
    def is_english_job(self, text):
        """简单英文检测"""
        if not text:
            return False, 0.0
        english_words = ['experience', 'skills', 'team', 'project', 'development']
        text_lower = text.lower()
        matches = sum(1 for word in english_words if word in text_lower)
        score = matches / len(english_words)
        return score >= 0.4, round(score, 2)
    
    def test_connection(self):
        """测试连接和登录状态"""
        try:
            print("🌐 测试访问LinkedIn...")
            self.driver.get("https://www.linkedin.com")
            time.sleep(5)
            
            # 检查是否在登录状态
            current_url = self.driver.current_url
            if "feed" in current_url or "jobs" in current_url:
                print("✅ 已处于登录状态")
                return True
            else:
                print("❌ 需要登录")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False
    
    def scrape_jobs_simple(self):
        """简化版爬取"""
        try:
            # 先测试连接
            if not self.test_connection():
                self.wait_for_manual_login()
            
            # 访问搜索页面
            print("🔍 访问搜索页面...")
            search_url = self.build_search_url()
            self.driver.get(search_url)
            time.sleep(8)
            
            # 检查是否有职位列表
            try:
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
                print(f"📊 找到 {len(job_elements)} 个职位")
                
                if not job_elements:
                    print("❌ 没有找到职位列表，可能页面未正确加载")
                    return
                    
            except Exception as e:
                print(f"❌ 查找职位列表失败: {e}")
                return
            
            # 只处理前几个职位测试
            for i in range(min(3, len(job_elements))):
                try:
                    print(f"\n📋 处理第 {i+1} 个职位")
                    
                    # 点击职位
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
                    if i >= len(job_elements):
                        break
                        
                    job_elements[i].click()
                    time.sleep(3)
                    
                    # 提取基本信息
                    job_info = self.extract_simple_info()
                    if job_info:
                        is_english, score = self.is_english_job(job_info.get('description', ''))
                        job_info['is_english'] = is_english
                        job_info['english_score'] = score
                        
                        self.jobs_data.append(job_info)
                        print(f"   ✅ 成功提取: {job_info['title']}")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️ 处理职位 {i+1} 失败: {e}")
                    continue
            
            print(f"\n🎉 成功处理 {len(self.jobs_data)} 个职位")
            
        except Exception as e:
            print(f"❌ 爬取过程出错: {e}")
    
    def extract_simple_info(self):
        """简化信息提取"""
        try:
            info = {}
            
            # 标题
            try:
                title_elements = self.driver.find_elements(By.TAG_NAME, "h2")
                for elem in title_elements:
                    text = elem.text.strip()
                    if text and len(text) > 5:
                        info['title'] = text
                        break
                if 'title' not in info:
                    info['title'] = "Unknown"
            except:
                info['title'] = "Unknown"
            
            # 公司
            try:
                company_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-tracking-control-name='public_jobs_jserp-result_job-search-card-subtitle']")
                if company_elements:
                    info['company'] = company_elements[0].text.strip()
                else:
                    info['company'] = "Unknown"
            except:
                info['company'] = "Unknown"
            
            # 地点
            try:
                location_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='location'], [data-tracking-control-name*='location']")
                if location_elements:
                    info['location'] = location_elements[0].text.strip()
                else:
                    info['location'] = "Unknown"
            except:
                info['location'] = "Unknown"
            
            # 描述
            try:
                desc_elements = self.driver.find_elements(By.ID, "job-details")
                if desc_elements:
                    info['description'] = desc_elements[0].text.strip()
                else:
                    info['description'] = ""
            except:
                info['description'] = ""
            
            info['job_url'] = self.driver.current_url
            info['scraped_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return info
            
        except Exception as e:
            print(f"⚠️ 提取信息失败: {e}")
            return None
    
    def save_results(self):
        """保存结果"""
        if not self.jobs_data:
            print("❌ 没有数据可保存")
            return False
        
        try:
            df = pd.DataFrame(self.jobs_data)
            filename = "test_jobs.xlsx"
            
            # 确保有必要的列
            if 'title' not in df.columns:
                df['title'] = 'Unknown'
            if 'company' not in df.columns:
                df['company'] = 'Unknown'
            if 'location' not in df.columns:
                df['location'] = 'Unknown'
            
            df.to_excel(filename, index=False)
            print(f"💾 成功保存到: {filename}")
            print(f"📊 保存了 {len(df)} 行数据")
            return True
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔚 浏览器已关闭")

def main():
    print("=" * 50)
    print("🔧 LinkedIn调试版")
    print("=" * 50)
    
    scraper = SimpleLinkedInScraper()
    
    try:
        # 1. 启动浏览器
        if not scraper.setup_driver():
            return
        
        # 2. 爬取数据
        scraper.scrape_jobs_simple()
        
        # 3. 保存结果
        if scraper.jobs_data:
            success = scraper.save_results()
            if success:
                print("\n🎯 调试完成！检查 test_jobs.xlsx 文件")
            else:
                print("\n❌ 保存失败")
        else:
            print("\n❌ 没有获取到数据")
            
    except Exception as e:
        print(f"💥 程序出错: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
